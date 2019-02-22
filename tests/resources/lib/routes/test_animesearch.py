import os
import json
import unittest
from mock import call, patch, MagicMock, ANY
from resources.lib.constants.url import BASE_URL, SEARCH_PATH

class TestAnimeSearch(unittest.TestCase):
    def setUp(self):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))

        self.mock_xbmc_gui = MagicMock()
        self.mock_xbmc_plugin = MagicMock()

        self.mock_xbmc_addon_inst = MagicMock()
        self.mock_xbmc_addon_inst.getAddonInfo.return_value = "Addon ID"
        self.mock_xbmc_addon = MagicMock()
        self.mock_xbmc_addon.Addon.return_value = self.mock_xbmc_addon_inst

        self.mock_requests = MagicMock()

        self.mock_route_factory = MagicMock()
        self.mock_episode_list = MagicMock()

        modules = {
            "requests": self.mock_requests,
            "xbmcplugin": self.mock_xbmc_plugin,
            "xbmcgui": self.mock_xbmc_gui,
            "xbmcaddon": self.mock_xbmc_addon,
            "resources.lib.routes.episodelist": self.mock_episode_list,
            "resources.lib.router_factory": self.mock_route_factory
        }

        self.module_patcher = patch.dict('sys.modules', modules)
        self.module_patcher.start()

    def tearDown(self):
        self.module_patcher.stop()

    def test_route_generation(self):
        mock_plugin = MagicMock()
        
        from resources.lib.routes.animesearch import generate_routes, anime_search

        generate_routes(mock_plugin)

        mock_plugin.add_route.assert_has_calls([
            call(anime_search, "/search")
        ])

    def search_result_common_checks(self, mock_plugin, mock_list_item, animesearch, search_params, next_page=True):
        next_page_info = {
            "url_for": [call(animesearch, **search_params)] if next_page else [],
            "list_item": [call("Next Page")] if next_page else [],
            "directory_item": [call(mock_plugin.handle, ANY, ANY, True)] if next_page else []
        }

        mock_plugin.url_for.assert_has_calls([
            call(self.mock_episode_list.episode_list, id="10202", listId="8578", episode_count="1"),
            call(self.mock_episode_list.episode_list, id="10292", listId="8801", episode_count="13"),
            call(self.mock_episode_list.episode_list, id="13075", listId="8802", episode_count="13")
        ] + next_page_info.get("url_for"))

        self.mock_xbmc_gui.ListItem.assert_has_calls([
            call("Akuma no Riddle: Shousha wa Dare? Nukiuchi Test"),
            call().setArt({"icon": "https://myanimelist.cdn-dena.com/images/anime/11/63653.jpg"}),
            call().setInfo(type="video", infoLabels={"plot": "Unaired episode 13 of Akuma no Riddle released with the seventh Blu-ray/DVD volume.\r\n\r\nThe special will be previewed at a screening in Tokyo City on November 22, 2014. The BD/DVD will be released on December 17, 2014. "}),
            call("Baka to Test to Shoukanjuu "),
            call().setArt({"icon": "https://myanimelist.cdn-dena.com/images/anime/3/50389.jpg"}),
            call().setInfo(type="video", infoLabels={"plot": "The story centers around Akihisa Yoshii, the \"baka\" of the title. His academy rigidly divides up the student body into classes based on the results of tests. The prodigies are in the A class with reclining seats complete with air conditioning, but Akihisa is in F class, the lowest rung of the school ladder which is furnished only with low, decrepit tables and worn-out straw tatami mats. A girl named Mizuki Himeji is actually one of the smartest girls in Akihisa's sophomore year, but she had a fever on test day and was pigeonholed into the F class. Besides Mizuki (who Akihisa secretly adores), the F class also has Yuuji Sakamoto, the class president who has been Akihisa's friend and partner-in-crime since the freshman year.\r\n\r\nThe school happens to have developed experiments to summon fantasy creatures, and Akihisa decides to rally F class to take on the higher-tiered classes and seize their perks. The F class uses the summoned creatures in an all-out battle for school supremacy."}),
            call("Baka to Test to Shoukanjuu (Dub)"),
            call().setArt({"icon": "https://myanimelist.cdn-dena.com/images/anime/3/50389.jpg"}),
            call().setInfo(type="video", infoLabels={"plot": "The story centers around Akihisa Yoshii, the \"baka\" of the title. His academy rigidly divides up the student body into classes based on the results of tests. The prodigies are in the A class with reclining seats complete with air conditioning, but Akihisa is in F class, the lowest rung of the school ladder which is furnished only with low, decrepit tables and worn-out straw tatami mats. A girl named Mizuki Himeji is actually one of the smartest girls in Akihisa's sophomore year, but she had a fever on test day and was pigeonholed into the F class. Besides Mizuki (who Akihisa secretly adores), the F class also has Yuuji Sakamoto, the class president who has been Akihisa's friend and partner-in-crime since the freshman year.\r\n\r\nThe school happens to have developed experiments to summon fantasy creatures, and Akihisa decides to rally F class to take on the higher-tiered classes and seize their perks. The F class uses the summoned creatures in an all-out battle for school supremacy."})
        ] + next_page_info.get("list_item"))

        self.mock_xbmc_plugin.addDirectoryItem.assert_has_calls([
            call(mock_plugin.handle, ANY, ANY, True),
            call(mock_plugin.handle, ANY, ANY, True),
            call(mock_plugin.handle, ANY, ANY, True),
        ] + next_page_info.get("directory_item"))

        self.mock_xbmc_plugin.endOfDirectory.assert_called_once_with(mock_plugin.handle)

    def test_search_success_no_page(self):
        expected_search = "TestSearch"
        mock_plugin = type('', (), {})
        mock_plugin.handle = "Test"
        mock_plugin.args = {
            "name": [expected_search]
        }

        mock_plugin.url_for = MagicMock()

        self.mock_route_factory.get_router_instance.return_value = mock_plugin

        fixture_path = self.dir_path + "/fixtures/animesearch/success.json"

        with open(fixture_path, "r") as fixture:
            mock_response = fixture.read()

        self.mock_requests.get.return_value.json.return_value = json.loads(mock_response)

        mock_list_item = MagicMock()
        self.mock_xbmc_gui.ListItem.return_value = mock_list_item

        from resources.lib.routes.animesearch import anime_search

        anime_search()

        expected_params = {
            "name": expected_search,
            "page": 1,
            "limit": 10
        }

        self.mock_requests.get.assert_called_once_with(BASE_URL + SEARCH_PATH, params=expected_params)
        self.search_result_common_checks(mock_plugin, mock_list_item, anime_search, { "name": expected_search, "page": "2" })

    def test_search_success_no_search(self):
        expected_search = "TestSearch"
        mock_plugin = type('', (), {})
        mock_plugin.handle = "Test"
        mock_plugin.args = {}

        mock_plugin.url_for = MagicMock()

        self.mock_route_factory.get_router_instance.return_value = mock_plugin

        fixture_path = self.dir_path + "/fixtures/animesearch/success.json"

        with open(fixture_path, "r") as fixture:
            mock_response = fixture.read()

        self.mock_requests.get.return_value.json.return_value = json.loads(mock_response)

        mock_list_item = MagicMock()
        self.mock_xbmc_gui.ListItem.return_value = mock_list_item

        from resources.lib.routes.animesearch import anime_search

        anime_search()

        expected_params = {
            "name": '',
            "page": 1,
            "limit": 10
        }

        self.mock_requests.get.assert_called_once_with(BASE_URL + SEARCH_PATH, params=expected_params)
        self.search_result_common_checks(mock_plugin, mock_list_item, anime_search, { "name": '', "page": "2" })

    def test_search_success_page_passed_no_next(self):
        expected_search = "TestSearch"
        mock_plugin = type('', (), {})
        mock_plugin.handle = "Test"
        mock_plugin.args = {
            "name": [expected_search],
            "page": ["5"]
        }

        mock_plugin.url_for = MagicMock()

        self.mock_route_factory.get_router_instance.return_value = mock_plugin

        fixture_path = self.dir_path + "/fixtures/animesearch/success.json"

        with open(fixture_path, "r") as fixture:
            mock_response = fixture.read()

        self.mock_requests.get.return_value.json.return_value = json.loads(mock_response)

        mock_list_item = MagicMock()
        self.mock_xbmc_gui.ListItem.return_value = mock_list_item

        from resources.lib.routes.animesearch import anime_search

        anime_search()

        expected_params = {
            "name": expected_search,
            "page": 5,
            "limit": 10
        }

        self.mock_requests.get.assert_called_once_with(BASE_URL + SEARCH_PATH, params=expected_params)
        self.search_result_common_checks(mock_plugin, mock_list_item, anime_search, { "name": expected_search }, False)
