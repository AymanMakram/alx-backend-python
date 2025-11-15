#!/usr/bin/env python3
"""Unit tests for GithubOrgClient in client.py"""
import unittest
from parameterized import parameterized, parameterized_class
from unittest.mock import patch, PropertyMock
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Tests for GithubOrgClient"""

    @patch('client.get_json')

    def test_public_repos(self, mock_get_json):
        """Test GithubOrgClient.public_repos returns expected repos list"""
        # Mock payload returned by get_json
        repo_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": {"key": "mit"}},
        ]
        mock_get_json.return_value = repo_payload
        client = GithubOrgClient("test_org")
        # Patch the _public_repos_url property to a dummy URL
        with patch.object(
            GithubOrgClient,
            "_public_repos_url",
            new_callable=PropertyMock,
        ) as mock_repo_url:
            mock_repo_url.return_value = (
                "https://api.github.com/orgs/test_org/repos"
            )
            # Test without license filter
            expected_repos = ["repo1", "repo2", "repo3"]
            self.assertEqual(client.public_repos(), expected_repos)
            # Test with license filter
            expected_mit_repos = ["repo1", "repo3"]
            self.assertEqual(
                client.public_repos(license="mit"), expected_mit_repos
            )
            # Ensure the mocked property was accessed once
            mock_repo_url.assert_called_once()
        # Ensure get_json was called once with the mocked URL
        mock_get_json.assert_called_once_with(
            "https://api.github.com/orgs/test_org/repos"
        )
    # ============================================================
    # 7. test_has_license
    # ============================================================
    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])

    def test_has_license(self, repo, license_key, expected):
        """Test has_license"""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


    @patch('client.GithubOrgClient.repos', new_callable=PropertyMock)
    def test_public_repos(self, mock_repos):
        """
        Tests that public_repos returns the expected list of public repository names
        when no license filter is applied.
        """
        # Set the mock return value to the list of repositories from the fixture
        REPOS_PAYLOAD = TEST_PAYLOAD[0][1]
        mock_repos.return_value = REPOS_PAYLOAD

        # The expected result is the list of 'name' values for all repos
        expected_repos = [
            repo["name"]
            for repo in REPOS_PAYLOAD
        ]

        # Instantiate the client and call the method under test
        client = GithubOrgClient("google")
        result = client.public_repos()

        # Assert that the result matches the expected list of names
        self.assertEqual(result, expected_repos)

        # Assert that the mock property was accessed exactly once
        mock_repos.assert_called_once()

    @patch('client.GithubOrgClient.repos', new_callable=PropertyMock)
    def test_public_repos_with_license(self, mock_repos):
        """
        Tests public_repos with the license filter set to 'apache-2.0',
        ensuring only repos with that license are returned.
        """
        # Setup mock return value (the full list of repos)
        REPOS_PAYLOAD = TEST_PAYLOAD[0][1]
        mock_repos.return_value = REPOS_PAYLOAD

        # Define expected result: only repos with license key 'apache-2.0'
        # Based on the fixture, this is ['firmata.py']
        expected_repos = [
            repo["name"]
            for repo in REPOS_PAYLOAD
            if repo.get("license", {}).get("key") == "apache-2.0"
        ]

        # Instantiate the client and call the method under test with the license argument
        client = GithubOrgClient("google")
        result = client.public_repos(license="apache-2.0")

        # Assert that the result matches the expected filtered list
        self.assertEqual(result, expected_repos)

        # Assert that the mock was accessed exactly once
        mock_repos.assert_called_once()

# ============================================================
# 8. Integration Tests
# ============================================================
@parameterized_class(("repos_payload", "expected_repos", "apache2_repos"), TEST_PAYLOAD)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient"""

    @classmethod
    def setUpClass(cls):
        """Mock requests.get at the class level"""
        cls.get_patcher = patch("requests.get")
        mock_get = cls.get_patcher.start()

        # Simulate sequential .json() calls
        mock_get.return_value.json.side_effect = [
            cls.org_payload,     # response for org()
            cls.repos_payload,   # response for repos_payload()
            cls.repos_payload,   # response for second repos payload access
        ]

    @classmethod
    def tearDownClass(cls):
        """Stop patcher"""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos returns full list"""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Test public_repos filters by license"""
        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos("apache-2.0"),
            self.apache2_repos
        )

    @patch('client.GithubOrgClient.repos', new_callable=PropertyMock)

    def test_public_repos(self, mock_repos):
        """
        Tests that public_repos returns the expected list of public repository names
        when no license filter is applied.
        """
        # Set the mock return value to the list of repositories from the fixture
        REPOS_PAYLOAD = TEST_PAYLOAD[0][1]
        mock_repos.return_value = REPOS_PAYLOAD
        # The expected result is the list of 'name' values for all repos
        expected_repos = [
            repo["name"] for repo in REPOS_PAYLOAD
        ]
        # Instantiate the client and call the method under test
        client = GithubOrgClient("google")
        result = client.public_repos()
        # Assert that the result matches the expected list of names
        self.assertEqual(result, expected_repos)
        # Assert that the mock property was accessed exactly once
        mock_repos.assert_called_once()

if __name__ == "__main__":
    unittest.main()
