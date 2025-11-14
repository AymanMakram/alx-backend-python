#!/usr/bin/env python3
"""Test module for client.py"""
import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Test cases for GithubOrgClient class"""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns the correct value"""
        # Define expected return value
        expected_payload = {"login": org_name, "id": 12345}
        mock_get_json.return_value = expected_payload

        # Create client and call org
        client = GithubOrgClient(org_name)
        result = client.org

        # Assert get_json was called once with the correct URL
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)

        # Assert the result is what we expect
        self.assertEqual(result, expected_payload)

    def test_public_repos_url(self):
        """
        Test that _public_repos_url returns the expected value.
        
        Uses patch as a context manager to mock the org property
        and verify _public_repos_url extracts the correct URL.
        """
        # Known payload with repos_url
        known_payload = {
            "login": "google",
            "id": 1342004,
            "repos_url": "https://api.github.com/orgs/google/repos"
        }

        # Patch the org property to return our known payload
        # Use PropertyMock since org is a property (memoized method)
        with patch.object(
            GithubOrgClient,
            'org',
            new_callable=PropertyMock,
            return_value=known_payload
        ):
            # Create client instance
            client = GithubOrgClient("google")
            
            # Access _public_repos_url property
            result = client._public_repos_url

            # Assert the result matches the repos_url from payload
            self.assertEqual(result, known_payload["repos_url"])

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """
        Test that public_repos returns the expected list of repos.
        
        Uses:
        - @patch decorator to mock get_json
        - patch context manager to mock _public_repos_url property
        
        Verifies:
        - Returned list matches expected repo names
        - get_json called once
        - _public_repos_url accessed once
        """
        # Define test payload - list of repos returned by get_json
        test_repos_payload = [
            {"name": "episodes.dart", "license": {"key": "bsd-3-clause"}},
            {"name": "cpp-netlib", "license": {"key": "bsl-1.0"}},
            {"name": "dagger", "license": {"key": "apache-2.0"}},
            {"name": "ios-webkit-debug-proxy", "license": {"key": "other"}},
        ]
        
        # Expected repo names extracted from payload
        expected_repos = [
            "episodes.dart",
            "cpp-netlib",
            "dagger",
            "ios-webkit-debug-proxy"
        ]
        
        # Configure mock_get_json to return our test payload
        mock_get_json.return_value = test_repos_payload
        
        # Use patch as context manager to mock _public_repos_url property
        with patch.object(
            GithubOrgClient,
            '_public_repos_url',
            new_callable=PropertyMock,
            return_value="https://api.github.com/orgs/google/repos"
        ) as mock_public_repos_url:
            
            # Create client and call public_repos
            client = GithubOrgClient("google")
            result = client.public_repos()
            
            # Test 1: Verify the list of repos matches expected
            self.assertEqual(result, expected_repos)
            
            # Test 2: Verify _public_repos_url property was accessed once
            mock_public_repos_url.assert_called_once()
            
            # Test 3: Verify get_json was called once
            mock_get_json.assert_called_once()


if __name__ == '__main__':
    unittest.main()

    def test_public_repos_url(self):
        """Test that _public_repos_url returns expected value"""
        # Known payload with repos_url
        known_payload = {
            "login": "google",
            "id": 1342004,
            "repos_url": "https://api.github.com/orgs/google/repos"
        }

        # Patch the org property to return our known payload
        with patch.object(
            GithubOrgClient,
            'org',
            new_callable=PropertyMock,
            return_value=known_payload
        ):
            client = GithubOrgClient("google")
            result = client._public_repos_url

            # Assert the result matches the repos_url from payload
            self.assertEqual(result, known_payload["repos_url"])

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """
        Test that public_repos returns expected list of repos.
        
        This test:
        1. Mocks get_json to return a specific repos payload
        2. Mocks _public_repos_url to return a test URL
        3. Verifies the repo names list matches expected output
        4. Verifies both mocks were called exactly once
        """
        # Define test payload - list of repos with names
        test_repos_payload = [
            {"name": "episodes.dart", "license": {"key": "bsd-3-clause"}},
            {"name": "cpp-netlib", "license": {"key": "bsl-1.0"}},
            {"name": "dagger", "license": {"key": "apache-2.0"}},
        ]
        
        # Expected repo names from our payload
        expected_repos = ["episodes.dart", "cpp-netlib", "dagger"]
        
        # Mock get_json to return our test payload
        mock_get_json.return_value = test_repos_payload
        
        # Use patch as context manager to mock _public_repos_url property
        with patch.object(
            GithubOrgClient,
            '_public_repos_url',
            new_callable=PropertyMock,
            return_value="https://api.github.com/orgs/google/repos"
        ) as mock_public_repos_url:
            
            # Create client and get public repos
            client = GithubOrgClient("google")
            result = client.public_repos()
            
            # Test 1: Verify the list of repos matches expected
            self.assertEqual(result, expected_repos)
            
            # Test 2: Verify _public_repos_url was called once
            mock_public_repos_url.assert_called_once()
            
            # Test 3: Verify get_json was called once
            mock_get_json.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test that has_license returns correct boolean value"""
        client = GithubOrgClient("google")
        result = client.has_license(repo, license_key)
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()