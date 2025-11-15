#!/usr/bin/env python3
import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized, parameterized_class

from client import GithubOrgClient
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos


# ============================================================
# 6. TEST PUBLIC_REPOS (unit test)
# ============================================================
class TestGithubOrgClient(unittest.TestCase):

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """Test GithubOrgClient.public_repos"""

        # Mock get_json return value
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

            # Expected result
            self.assertEqual(result, ["repo1", "repo2"])

            # Ensure mocks called once
            mock_url.assert_called_once()
            mock_get_json.assert_called_once_with("http://fake-url")

    # ============================================================
    # 7. PARAMETERIZE has_license
    # ============================================================
    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test GithubOrgClient.has_license"""
        self.assertEqual(
            GithubOrgClient.has_license(repo, license_key),
            expected
        )


# ============================================================
# 8. INTEGRATION TESTS (fixtures)
# ============================================================
@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    [
        (org_payload, repos_payload, expected_repos, apache2_repos),
    ],
)
class TestIntegrationGithubOrgClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Mock requests.get using fixtures"""

        cls.get_patcher = patch("requests.get")
        mock_get = cls.get_patcher.start()

        # Return values for each call to requests.get().json()
        mock_get.return_value.json.side_effect = [
            cls.org_payload,
            cls.repos_payload,
            cls.repos_payload,
        ]

    @classmethod
    def tearDownClass(cls):
        """Stop patcher"""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Integration: test public_repos"""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Integration: test public_repos filtering by license"""
        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos("apache-2.0"),
            self.apache2_repos
        )
