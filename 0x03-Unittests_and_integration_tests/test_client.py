#!/usr/bin/env python3
"""
Unit tests for client.GithubOrgClient
"""
import unittest
from parameterized import parameterized
from unittest.mock import patch, Mock
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Test cases for GithubOrgClient."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json", return_value={"key": "value"})
    def test_org(self, org_name: str, mock_get_json: Mock) -> None:
        """Test that GithubOrgClient.org returns the expected result."""
        client = GithubOrgClient(org_name)
        result = client.org
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )
        self.assertEqual(result, {"key": "value"})

    def test_public_repos_url(self):
        """Test that _public_repos_url returns the correct URL
        based on the mocked org payload.
        """
        expected_url = "https://api.github.com/orgs/testorg/repos"
        payload = {"repos_url": expected_url}

        # Patch GithubOrgClient.org as a property
        with patch("client.GithubOrgClient.org",
                   new_callable=PropertyMock,
                   return_value=payload):

            client = GithubOrgClient("testorg")
            result = client._public_repos_url

            self.assertEqual(result, expected_url)
    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """Test GithubOrgClient.public_repos returns expected repo list and
        ensures mocked methods were called exactly once.
        """
        # Mock JSON payload returned by get_json
        mock_payload = [
            {"name": "repo1"},
            {"name": "repo2"},
            {"name": "repo3"},
        ]
        mock_get_json.return_value = mock_payload

        # URL to be returned by _public_repos_url
        mock_url = "https://api.github.com/orgs/testorg/repos"

        with patch("client.GithubOrgClient._public_repos_url",
                   new_callable=PropertyMock,
                   return_value=mock_url) as mock_url_prop:

            client = GithubOrgClient("testorg")
            result = client.public_repos()

            # Expected repo names extracted from mock_payload
            expected = ["repo1", "repo2", "repo3"]

            self.assertEqual(result, expected)

            # Ensure each mock was called exactly once
            mock_url_prop.assert_called_once()
            mock_get_json.assert_called_once_with(mock_url)

if __name__ == "__main__":
    unittest.main()
