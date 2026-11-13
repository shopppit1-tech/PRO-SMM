import os
import unittest
from unittest.mock import patch

from peakerr_client import PeakerrAPIError, PeakerrClient


class PeakerrClientTests(unittest.TestCase):
    def test_requires_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(PeakerrAPIError):
                PeakerrClient.from_environment()

    def test_endpoint_can_be_overridden(self):
        with patch.dict(
            os.environ,
            {"PEAKERR_API_KEY": "test-key", "PEAKERR_API_URL": "https://example.test/api"},
            clear=True,
        ):
            client = PeakerrClient.from_environment()
            self.assertEqual(client.endpoint, "https://example.test/api")


if __name__ == "__main__":
    unittest.main()
