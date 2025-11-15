#!/usr/bin/env python3
import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient



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

