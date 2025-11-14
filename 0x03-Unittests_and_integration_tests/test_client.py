#!/usr/bin/env python3
"""
Unit tests for GithubOrgClient
"""

import unittest
from unittest.mock import patch, PropertyMock, MagicMock
from parameterized import parameterized
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Tests for GithubOrgClient"""

    @parameterized.expand([
        ("google", {"payload": True}),
        ("abc", {"payload": False}),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, payload, mock_get_json):
        """Test GithubOrgClient.org"""
        mock_get_json.return_value = payload
        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, payload)
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

    def test_public_repos_url(self):
        """Test _public_repos_url property"""
        with patch(
            "client.GithubOrgClient.org",
            new_callable=PropertyMock
        ) as mock_org:
            mock_org.return_value = {"repos_url": "https://api.github.com/orgs/test/repos"}

            client = GithubOrgClient("test")
            self.assertEqual(client._public_repos_url,
                             "https://api.github.com/orgs/test/repos")

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
       """Test public_repos method"""
       mock_payload = [
        {"name": "repo1"},
        {"name": "repo2"},
        {"name": "repo3"},
     ]
       mock_get_json.return_value = mock_payload

       with patch(
        "client.GithubOrgClient._public_repos_url",
        new_callable=PropertyMock
        ) as mock_repos_url:

         mock_repos_url.return_value = "http://example.com/repos"
         client = GithubOrgClient("test")
         result = client.public_repos()

       expected = ["repo1", "repo2", "repo3"]
       self.assertEqual(result, expected)

       mock_get_json.assert_called_once()
       mock_repos_url.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "apache-2.0"}}, "apache-2.0", True),
        ({"license": {"key": "mit"}}, "apache-2.0", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test has_license"""
        self.assertEqual(
            GithubOrgClient.has_license(repo, license_key),
            expected
        )

    @patch("client.get_json")
    def test_public_repos_with_license(self, mock_get_json):
        """Test filtering repos by license"""
        payload = [
            {"name": "repo1", "license": {"key": "apache-2.0"}},
            {"name": "repo2", "license": {"key": "mit"}},
            {"name": "repo3", "license": {"key": "apache-2.0"}},
        ]

        mock_get_json.return_value = payload

        with patch(
            "client.GithubOrgClient._public_repos_url",
            new_callable=PropertyMock
        ) as mock_repos_url:

            mock_repos_url.return_value = "dummy-url"

            client = GithubOrgClient("test")
            result = client.public_repos(license="apache-2.0")

        expected = ["repo1", "repo3"]
        self.assertEqual(result, expected)

        mock_get_json.assert_called_once()
        mock_repos_url.assert_called_once()


class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests (task 6)"""

    @classmethod
    def setUpClass(cls):
        """Mock get_json and org payload"""
        cls.get_patcher = patch("client.get_json", return_value=TEST_PAYLOAD[0][1])
        cls.mock_get_json = cls.get_patcher.start()

        cls.repos_url_patcher = patch(
            "client.GithubOrgClient._public_repos_url",
            new_callable=PropertyMock,
            return_value=TEST_PAYLOAD[0][1]["repos_url"]
        )
        cls.mock_repos_url = cls.repos_url_patcher.start()

    @classmethod
    def tearDownClass(cls):
        """Stop all patches"""
        cls.get_patcher.stop()
        cls.repos_url_patcher.stop()

    def test_public_repos(self):
        """Integration test for public_repos"""
        client = GithubOrgClient("google")
        expected = [repo["name"] for repo in TEST_PAYLOAD[1][1]]
        self.assertEqual(client.public_repos(), expected)

    def test_public_repos_with_license(self):
        """Integration test filtering by license"""
        client = GithubOrgClient("google")
        expected = [
            repo["name"]
            for repo in TEST_PAYLOAD[1][1]
            if repo["license"]["key"] == "apache-2.0"
        ]
        self.assertEqual(client.public_repos("apache-2.0"), expected)

if __name__ == "__main__":
    unittest.main()
