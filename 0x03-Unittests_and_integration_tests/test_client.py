#!/usr/bin/env python3
"""Test module for GithubOrgClient"""

import unittest
from unittest.mock import patch, PropertyMock, MagicMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
import fixtures


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient"""

    @parameterized(["google", "abc"])
    @patch("client.get_json")
    def test_org(self, org, mock_get_json):
        """Test org method"""
        client = GithubOrgClient(org)
        client.org
        mock_get_json.assert_called_once_with(f"https://api.github.com/orgs/{org}")

    def test_public_repos_url(self):
        """Test _public_repos_url property"""
        with patch("client.GithubOrgClient.org", new_callable=PropertyMock) as mock_org:
            mock_org.return_value = {"repos_url": "http://some_url.com"}
            client = GithubOrgClient("google")
            self.assertEqual(client._public_repos_url, "http://some_url.com")

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """Test public_repos returns expected repo names"""
        mock_get_json.return_value = fixtures.repos_payload

        with patch("client.GithubOrgClient._public_repos_url",
                   new_callable=PropertyMock) as mock_url:
            mock_url.return_value = "http://example.com/repos"

            client = GithubOrgClient("google")
            result = client.public_repos()

            self.assertEqual(result, fixtures.expected_repos)
            mock_url.assert_called_once()

    @patch("client.get_json")
    def test_public_repos_with_license(self, mock_get_json):
        """Test filtering public_repos by license='apache-2.0'"""
        mock_get_json.return_value = fixtures.repos_payload

        with patch("client.GithubOrgClient._public_repos_url",
                   new_callable=PropertyMock) as mock_url:
            mock_url.return_value = "http://example.com/repos"

            client = GithubOrgClient("google")
            result = client.public_repos(license="apache-2.0")

            self.assertEqual(result, fixtures.apache2_repos)
            mock_url.assert_called_once()

    @parameterized([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test has_license utility method"""
        client = GithubOrgClient("google")
        self.assertEqual(client.has_license(repo, license_key), expected)


# ----------------------------------------------------------------------
#   INTEGRATION TESTS
# ----------------------------------------------------------------------

@parameterized_class([
    {
        "org_payload": fixtures.org_payload,
        "repos_payload": fixtures.repos_payload,
        "expected_repos": fixtures.expected_repos,
        "apache2_repos": fixtures.apache2_repos,
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient using fixtures"""

    @classmethod
    def setUpClass(cls):
        """Start patching requests.get with fixture-based responses"""
        cls.get_patcher = patch("requests.get")
        mock_get = cls.get_patcher.start()

        def get_json_side_effect(url):
            mock_response = MagicMock()

            if url.endswith("google"):
                mock_response.json.return_value = cls.org_payload

            elif url.endswith("google/repos"):
                mock_response.json.return_value = cls.repos_payload

            return mock_response

        mock_get.side_effect = get_json_side_effect

    @classmethod
    def tearDownClass(cls):
        """Stop patcher"""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos returns fixture-based results"""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Test public_repos filtered by apache-2.0 license"""
        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos
        )
