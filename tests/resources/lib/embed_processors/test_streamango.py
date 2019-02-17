import sys
import os
import unittest
from mock import MagicMock
from bs4 import BeautifulSoup

class TestStreamango(unittest.TestCase):
    def generate_mock_addon_inst(self, title):
        mock_addon_inst = MagicMock()
        mock_addon_inst.getAddonInfo = MagicMock(return_value="title")
        return mock_addon_inst

    def setUp(self):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))

        mock_addon = MagicMock()

        mock_addon_inst = self.generate_mock_addon_inst("title")
        mock_addon.Addon = MagicMock(return_value=mock_addon_inst)
        self.mock_addon = mock_addon

        sys.modules['xbmcaddon'] = self.mock_addon

    def test_successful_retrieval(self):
        fixture_path = self.dir_path + "/fixtures/streamango/streamango_success.html"

        with open(fixture_path, "r") as fixture:
            mock_response = fixture.read()

        soup = BeautifulSoup(mock_response, 'html.parser')
        
        from resources.lib.embed_processors import streamango

        (err, src_url) = streamango.retrieve_source_url(soup)
        self.assertIsNone(err)
        self.assertEqual(src_url, "https://streamango.com/v/d/mbaqfookertcmqar~1550457892~174.108.0.0~WKLsT61S/720")
      