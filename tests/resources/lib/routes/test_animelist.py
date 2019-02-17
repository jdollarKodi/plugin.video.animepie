import sys
import os
import json
import unittest
from mock import call, patch, MagicMock, Mock, ANY

# TODO: Check get params to ensure those match what is expected

class TestAnimeList(unittest.TestCase):
    def setUp(self):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))

        self.mock_requests = MagicMock()

        self.mock_xbmc_plugin = MagicMock()
        self.mock_xbmc_gui = MagicMock()

        modules = {
            "requests": self.mock_requests,
            "xbmcplugin": self.mock_xbmc_plugin,
            "xbmcgui": self.mock_xbmc_gui
        }

        self.module_patcher = patch.dict('sys.modules', modules)
        self.module_patcher.start()

    def tearDown(self):
        self.module_patcher.stop()

    def test_successful_retrieval_page_one_none_page(self):
        handle_val = "Random"
        mock_url = "Random-url"

        mock_plugin = type('', (), {})
        mock_plugin.handle = handle_val
        mock_plugin.url_for = Mock(return_value=mock_url)

        fixture_path = self.dir_path + "/fixtures/animeList/list_success.json"

        with open(fixture_path, "r") as fixture:
            mock_response = fixture.read()

        res_mock = MagicMock()
        res_mock.json = Mock(return_value=json.loads(mock_response))
        self.mock_requests.get = Mock(return_value=res_mock)

        from resources.lib.routes.animelist import anime_list
        anime_list(mock_plugin, None, "episode", "full")

        expected_list_item_calls = [
            call("Gintama.: Shirogane no Tamashii-hen 2"),
            call("Gintama.: Silver Soul Arc - Second Half War"),
            call("Gintama.: Shirogane no Tamashii-hen - Kouhan-sen"),
            call("Next Page"),
        ]

        # self.mock_xbmc_gui.ListItem.assert_has_calls(expected_list_item_calls)

        # Need to check for order of list items added
        expected_calls = [
            call(
                handle_val,
                mock_url,
                ANY,
                True
            ),
            call(
                handle_val,
                mock_url,
                ANY,
                True
            ),
            call(
                handle_val,
                mock_url,
                ANY,
                True
            ),
            call(
                handle_val,
                mock_url,
                ANY,
                True
            ),
        ]
        
        self.mock_xbmc_plugin.addDirectoryItem.assert_has_calls(expected_calls)

    def test_successful_retrieval_page_one_with_selected(self):
        handle_val = "Random"
        mock_url = "Random-url"

        mock_plugin = type('', (), {})
        mock_plugin.handle = handle_val
        mock_plugin.url_for = Mock(return_value=mock_url)

        fixture_path = self.dir_path + "/fixtures/animeList/list_success.json"

        with open(fixture_path, "r") as fixture:
            mock_response = fixture.read()

        res_mock = MagicMock()
        res_mock.json = Mock(return_value=json.loads(mock_response))
        self.mock_requests.get = Mock(return_value=res_mock)

        from resources.lib.routes.animelist import anime_list
        anime_list(mock_plugin, "1", "episode", "full")

        expected_list_item_calls = [
            call("Gintama.: Shirogane no Tamashii-hen 2"),
            call("Gintama.: Silver Soul Arc - Second Half War"),
            call("Gintama.: Shirogane no Tamashii-hen - Kouhan-sen"),
            call("Next Page"),
        ]

        self.mock_xbmc_gui.ListItem.assert_has_calls(expected_list_item_calls)

        # Need to check for order of list items added
        expected_calls = [
            call(
                handle_val,
                mock_url,
                ANY,
                True
            ),
            call(
                handle_val,
                mock_url,
                ANY,
                True
            ),
            call(
                handle_val,
                mock_url,
                ANY,
                True
            ),
            call(
                handle_val,
                mock_url,
                ANY,
                True
            ),
        ]
        
        self.mock_xbmc_plugin.addDirectoryItem.assert_has_calls(expected_calls)

    def test_successful_retrieval_no_next_on_last_page(self):
        handle_val = "Random"
        mock_url = "Random-url"

        mock_plugin = type('', (), {})
        mock_plugin.handle = handle_val
        mock_plugin.url_for = Mock(return_value=mock_url)

        fixture_path = self.dir_path + "/fixtures/animeList/list_success.json"

        with open(fixture_path, "r") as fixture:
            mock_response = fixture.read()

        res_mock = MagicMock()
        res_mock.json = Mock(return_value=json.loads(mock_response))
        self.mock_requests.get = Mock(return_value=res_mock)

        from resources.lib.routes.animelist import anime_list
        anime_list(mock_plugin, "8", "episode", "full")

        expected_list_item_calls = [
            call("Gintama.: Shirogane no Tamashii-hen 2"),
            call("Gintama.: Silver Soul Arc - Second Half War"),
            call("Gintama.: Shirogane no Tamashii-hen - Kouhan-sen"),
        ]

        self.assertEquals(self.mock_xbmc_gui.ListItem.call_count, 3)
        self.mock_xbmc_gui.ListItem.assert_has_calls(expected_list_item_calls)

        # Need to check for order of list items added
        expected_calls = [
            call(
                handle_val,
                mock_url,
                ANY,
                True
            ),
            call(
                handle_val,
                mock_url,
                ANY,
                True
            ),
            call(
                handle_val,
                mock_url,
                ANY,
                True
            ),
        ]
        
        self.assertEquals(self.mock_xbmc_plugin.addDirectoryItem.call_count, 3)
        self.mock_xbmc_plugin.addDirectoryItem.assert_has_calls(expected_calls)
