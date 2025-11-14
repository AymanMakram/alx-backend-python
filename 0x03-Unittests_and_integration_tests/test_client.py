#!/usr/bin/env python3
"""
Unit and Integration tests for the GithubOrgClient class in client.py.
"""
import unittest
from unittest.mock import patch, PropertyMock, Mock
from typing import Dict, List, Tuple
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """
    Tests for GithubOrgClient methods.
    """

    @parameterized.expand([
        ("google", {"login": "google"}),
        ("abc", {"login": "abc"}),
    ])
    @patch('client.get_json')
    def test_org(self, org_name: str, expected_org: Dict, mock_get_json: Mock) -> None:
        """
        Tests that GithubOrgClient.org returns the correct value
        and that get_json is called once with the correct URL.
        """
        mock_get_json.return_value = expected_org
        client = GithubOrgClient(org_name)
        result = client.org

        # Assert the result is the expected dictionary
        self.assertEqual(result, expected_org)

        # Assert that get_json was called once with the expected URL
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)

    def test_public_repos_url(self) -> None:
        """
        Tests that _public_repos_url returns the correct URL based on
        the mocked organization payload.
        """
        # Define the known payload for the mocked .org property
        expected_repos_url = "https://api.github.com/orgs/testorg/repos"
        mock_org_payload = {"repos_url": expected_repos_url}

        # Patch the 'org' property of GithubOrgClient using PropertyMock
        with patch.object(
            GithubOrgClient,
            'org',
            new_callable=PropertyMock,
            return_value=mock_org_payload
        ) as mock_org:
            client = GithubOrgClient("testorg")

            # Access the property being tested
            self.assertEqual(client._public_repos_url, expected_repos_url)

            # Ensure the mocked property was accessed once
            mock_org.assert_called_once()

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json: Mock) -> None:
        """
        Tests that public_repos returns the expected list of repo names.
        Mocks both _public_repos_url and get_json, and ensures they are called once.
        """
        # 1. Define the payloads
        mock_repos_payload: List[Dict] = [
            {"name": "repo1", "license": {"key": "apache-2.0"}},
            {"name": "repo2", "license": {"key": "mit"}},
            {"name": "repo3", "license": {"key": "apache-2.0"}},
            {"name": "repo4", "license": None},
        ]

        # 2. Configure mock_get_json
        mock_get_json.return_value = mock_repos_payload

        # 3. Define the mocked URL
        mock_url: str = "https://mock.repos.url"

        # 4. Patch '_public_repos_url' property using context manager
        with patch.object(
            GithubOrgClient,
            '_public_repos_url',
            new_callable=PropertyMock,
            return_value=mock_url
        ) as mock_public_repos_url:
            client = GithubOrgClient("testorg")

            # Test without license filter
            expected_repos_no_license: List[str] = ["repo1", "repo2", "repo3", "repo4"]
            self.assertEqual(client.public_repos(), expected_repos_no_license)

            # Test with license filter (apache-2.0)
            expected_repos_with_license: List[str] = ["repo1", "repo3"]
            self.assertEqual(client.public_repos("apache-2.0"), expected_repos_with_license)

            # Assert calls (called once due to memoization)
            mock_public_repos_url.assert_called_once()
            mock_get_json.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
        ({"license": {"key": "my_license"}}, "other_license", False),
        ({}, "my_license", False),
        ({"license": None}, "my_license", False),
        ({"license": {"key": None}}, "my_license", False),
    ])
    def test_has_license(
            self,
            repo: Dict,
            license_key: str,
            expected: bool
            ) -> None:
        """
        Tests the static method GithubOrgClient.has_license using parameterization.
        """
        self.assertEqual(
            GithubOrgClient.has_license(repo, license_key),
            expected
        )


# --- Integration Test Setup ---

# Unpack the fixtures from TEST_PAYLOAD for use with parameterized_class
# TEST_PAYLOAD[0] structure: (org_payload, repos_payload, expected_repos, apache2_repos)
org_payload, repos_payload, expected_repos, apache2_repos = TEST_PAYLOAD[0]

@parameterized_class([
    {
        'org_payload': org_payload,
        'repos_payload': repos_payload,
        'expected_repos': expected_repos,
        'apache2_repos': apache2_repos,
    },
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Integration tests for GithubOrgClient.public_repos, mocking only external requests.
    """

    @classmethod
    def setUpClass(cls):
        """
        Sets up class-level mock for requests.get to return fixture data.
        """
        # Start patching requests.get
        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()

        def side_effect(url: str):
            """
            Custom side effect function to return fixture data based on the requested URL.
            """
            mock_response = Mock()
            
            # Mock the organization URL request
            if url == GithubOrgClient.ORG_URL.format(org="google"):
                mock_response.json.return_value = cls.org_payload
            
            # Mock the repos URL request
            elif url == cls.org_payload["repos_url"]:
                mock_response.json.return_value = cls.repos_payload
            
            else:
                raise ValueError(f"Unexpected URL: {url}")
            
            return mock_response

        cls.mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """
        Tear down class method to stop the patcher.
        """
        cls.get_patcher.stop()

    def test_public_repos_no_license(self) -> None:
        """
        Tests public_repos without a license filter, relying on mocked network calls.
        """
        client = GithubOrgClient("google")
        # Assert that the list of all repo names matches the expected fixture data
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self) -> None:
        """
        Tests public_repos with a specific license filter (apache-2.0), 
        relying on mocked network calls.
        """
        client = GithubOrgClient("google")
        # Assert that the list of filtered repo names matches the expected fixture data
        self.assertEqual(client.public_repos("apache-2.0"), self.apache2_repos)