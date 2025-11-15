#!/usr/bin/env python3
"""
Unit tests for the client.py module.
"""
import unittest
from unittest.mock import patch, PropertyMock
from client import GithubOrgClient  # Assuming GithubOrgClient is in client.py
from fixtures import TEST_PAYLOAD  # Assuming fixtures.py is accessible

class TestGithubOrgClient(unittest.TestCase):
    """
    Tests the GithubOrgClient class.
    """
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

if __name__ == "__main__":
    unittest.main()