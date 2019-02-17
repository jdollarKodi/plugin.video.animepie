import sys
import unittest
from mock import MagicMock
from resources.lib.animepie_exception import AnimePieException

class TestMp4UploadProcessor(unittest.TestCase):
    def setUp(self):
      mock_addon = MagicMock()

      self.mock_js2py = MagicMock()
      self.mock_addon = mock_addon

      sys.modules['js2py'] = self.mock_js2py
      sys.modules['xbmcaddon'] = self.mock_addon

    def test_file_was_moved(self):
      localized_string = "test"

      mock_soup = MagicMock()
      mock_soup.find = MagicMock(return_value=None)

      mock_addon_inst = MagicMock()
      mock_addon_inst.getLocalizedString = MagicMock(return_value=localized_string)
      mock_addon_inst.getAddonInfo = MagicMock(return_value="title")
      self.mock_addon.Addon = MagicMock(return_value=mock_addon_inst)

      from resources.lib.embed_processors import mp4upload

      (err, src_url) = mp4upload.retrieve_source_url(mock_soup)
      self.assertIsInstance(err, AnimePieException)
      self.assertEqual(err.args[0], localized_string)
      self.assertIsNone(src_url)

    def test_source_url_extraction(self):
      self.assertEquals(False, True)
