from parameterized import parameterized_class
import unittest
from unittest.mock import patch, Mock
from client import GithubOrgClient
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos


@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    [
        (org_payload, repos_payload, expected_repos, apache2_repos)
    ]
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration test for GithubOrgClient.public_repos"""

    @classmethod
    def setUpClass(cls):
        """Start patcher for requests.get and return fixtures"""

        cls.get_patcher = patch("client.requests.get")
        cls.mock_get = cls.get_patcher.start()

        # Side effect to return correct fixture based on URL
        def side_effect(url):
            mock_response = Mock()

            # org payload request
            if url == f"https://api.github.com/orgs/{cls.org_payload['login']}":
                mock_response.json.return_value = cls.org_payload

            # repos payload request
            elif url == cls.org_payload["repos_url"]:
                mock_response.json.return_value = cls.repos_payload

            else:
                raise ValueError(f"Unexpected URL: {url}")

            return mock_response

        cls.mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """Stop patcher"""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos returns expected repos"""
        client = GithubOrgClient(self.org_payload["login"])
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Test filtering repos by 'apache-2.0' license"""
        client = GithubOrgClient(self.org_payload["login"])
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos
        )
