#!/usr/bin/env python3
"""Unit tests for GithubOrgClient in client.py"""
import unittest
from parameterized import parameterized, parameterized_class
from unittest.mock import patch, PropertyMock
from client import GithubOrgClient


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


if __name__ == "__main__":
    unittest.main()
