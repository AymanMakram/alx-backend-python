#!/usr/bin/env python3
import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized, parameterized_class

from client import GithubOrgClient
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient"""

    # ============================================================
    # 6. test_public_repos
    # ============================================================
    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """Test GithubOrgClient.public_repos"""

        # Mock returned JSON for repos
        mock_get_json.return_value = [
            {"name": "repo1"},
            {"name": "repo2"},
        ]

        # Mock _public_repos_url property
        with patch(
            "client.GithubOrgClient._public_repos_url",
            new_callable=PropertyMock
        ) as mock_url:

            mock_url.return_value = "http://fake-url"

            client = GithubOrgClient("google")
            result = client.public_repos()

            # Assert expected output
            self.assertEqual(result, ["repo1", "repo2"])

            # Assert mocks called correctly
            mock_url.assert_called_once()
            mock_get_json.assert_called_once_with("http://fake-url")

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


# ============================================================
# 8. Integration Tests
# ============================================================
@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    [
        (org_payload, repos_payload, expected_repos, apache2_repos),
    ],
)
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
