#!/usr/bin/env python3

import unittest
from unittest.mock import patch, PropertyMock
from client import GithubOrgClient  # Assuming GithubOrgClient is in client.py
from fixtures import TEST_PAYLOAD  # Assuming fixtures.py is accessible

class TestGithubOrgClient(unittest.TestCase):

    @patch('client.GithubOrgClient.repos', new_callable=PropertyMock)
    def test_public_repos(self, mock_repos):
        REPOS_PAYLOAD = TEST_PAYLOAD[0][1]
        mock_repos.return_value = REPOS_PAYLOAD
        expected_repos = [
            repo["name"]
            for repo in REPOS_PAYLOAD
        ]
        client = GithubOrgClient("google")
        result = client.public_repos()
        self.assertEqual(result, expected_repos)
        mock_repos.assert_called_once()

    @patch('client.GithubOrgClient.repos', new_callable=PropertyMock)
    def test_public_repos_with_license(self, mock_repos):
        REPOS_PAYLOAD = TEST_PAYLOAD[0][1]
        mock_repos.return_value = REPOS_PAYLOAD
        expected_repos = [
            repo["name"]
            for repo in REPOS_PAYLOAD
            if repo.get("license", {}).get("key") == "apache-2.0"
        ]
        client = GithubOrgClient("google")
        result = client.public_repos(license="apache-2.0")
        self.assertEqual(result, expected_repos)
        mock_repos.assert_called_once()

if __name__ == "__main__":
    unittest.main()