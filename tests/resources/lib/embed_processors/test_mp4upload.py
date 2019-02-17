import sys
import os
import unittest
from mock import MagicMock
from bs4 import BeautifulSoup
from resources.lib.animepie_exception import AnimePieException

class TestMp4UploadProcessor(unittest.TestCase):
    def generate_mock_addon_inst(self, localized_string, title):
      mock_addon_inst = MagicMock()
      mock_addon_inst.getLocalizedString = MagicMock(return_value=localized_string)
      mock_addon_inst.getAddonInfo = MagicMock(return_value="title")
      return mock_addon_inst

    def setUp(self):
      self.dir_path = os.path.dirname(os.path.realpath(__file__))

      mock_addon = MagicMock()

      self.mock_addon = mock_addon

      sys.modules['xbmcaddon'] = self.mock_addon

    def test_file_was_moved(self):
      localized_string = "test"
      fixture_path = self.dir_path + "/fixtures/mp4upload/mp4upload_file_deleted.html"

      with open(fixture_path, "r") as fixture:
        mock_empty_response = fixture.read()

      soup = BeautifulSoup(mock_empty_response, 'html.parser')

      mock_addon_inst = self.generate_mock_addon_inst(localized_string, "title")
      self.mock_addon.Addon = MagicMock(return_value=mock_addon_inst)

      from resources.lib.embed_processors import mp4upload

      (err, src_url) = mp4upload.retrieve_source_url(soup)
      self.assertIsInstance(err, AnimePieException)
      mock_addon_inst.getLocalizedString.assert_called_once_with(32000)
      self.assertEqual(err.args[0], localized_string)
      self.assertIsNone(src_url)

    def test_source_url_extraction(self):
      fixture_path = self.dir_path + "/fixtures/mp4upload/mp4upload_success.html"

      with open(fixture_path, "r") as fixture:
        mock_response = fixture.read()

      soup = BeautifulSoup(mock_response, 'html.parser')

      mock_addon_inst = self.generate_mock_addon_inst("test", "title")
      self.mock_addon.Addon = MagicMock(return_value=mock_addon_inst)

      from resources.lib.embed_processors import mp4upload

      (err, src_url) = mp4upload.retrieve_source_url(soup)
      self.assertIsNone(err)
      self.assertEqual(src_url, "https://www4.mp4upload.com:282/d/rcxxbfluz3b4quuor6va2psvjj4duz7tloglcecimbapilmbtxryrb3t/video.mp4")

