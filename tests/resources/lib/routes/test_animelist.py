import sys
import os
import json
import unittest
from mock import call, patch, MagicMock, Mock, ANY

# TODO: Check get params of request to ensure those match what is expected

class TestAnimeList(unittest.TestCase):
    def setUp(self):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))

        self.mock_requests = MagicMock()

        self.mock_xbmc_plugin = MagicMock()
        self.mock_xbmc_gui = MagicMock()

        self.mock_route_factory = MagicMock()

        modules = {
            "requests": self.mock_requests,
            "xbmcplugin": self.mock_xbmc_plugin,
            "xbmcgui": self.mock_xbmc_gui,
            "xbmcadddon": MagicMock(),
            "resolveurl": MagicMock(),
            "resources.lib.router_factory": self.mock_route_factory
        }

        self.module_patcher = patch.dict('sys.modules', modules)
        self.module_patcher.start()

    def tearDown(self):
        self.module_patcher.stop()

    def test_generate_routes(self):
        from resources.lib.routes.animelist import generate_routes, anime_list

        mock_plugin = MagicMock()

        generate_routes(mock_plugin)

        mock_plugin.add_route.assert_has_calls([
            call(anime_list, '/anime-list'),
        ])

    def test_get_current_params_returns_values_if_passed_in(self):
        from resources.lib.routes.animelist import _get_current_params

        expected_year = "2000"
        expected_season = "Winter"
        expected_genre = "Test,Test2"
        expected_page = "Page"

        mock_plugin = type('', (), {})
        mock_plugin.args = {
            "year": [expected_year],
            "season": [expected_season],
            "genres": [expected_genre],
            "page": [expected_page],
        }

        args = _get_current_params(mock_plugin)

        self.assertDictEqual(args, {
            "year": expected_year,
            "season": expected_season,
            "genres": expected_genre,
            "page": expected_page
        }, "Returned parameter list does not match plugin.arg values")

    def test_get_current_params_returns_empty_if_none(self):
        from resources.lib.routes.animelist import _get_current_params

        mock_plugin = type('', (), {})
        mock_plugin.args = {}

        args = _get_current_params(mock_plugin)

        self.assertDictEqual(args, {}, "Returned parameter list does not match plugin.arg values")

    def test_successful_retrieval_page_one_none_page(self):
        handle_val = "Random"
        mock_url = "Random-url"

        mock_plugin = type('', (), {})
        mock_plugin.args = {}
        mock_plugin.handle = handle_val
        mock_plugin.url_for = MagicMock()

        fixture_path = self.dir_path + "/fixtures/animeList/list_success.json"

        with open(fixture_path, "r") as fixture:
            mock_response = fixture.read()

        res_mock = MagicMock()
        res_mock.json.return_value = json.loads(mock_response)
        self.mock_requests.get.return_value = res_mock

        from resources.lib.routes.animelist import anime_list
        anime_list()

        self.mock_xbmc_gui.ListItem.assert_has_calls([
            call('Gintama.: Shirogane no Tamashii-hen 2'),
            call().setArt({'icon': 'https://myanimelist.cdn-dena.com/images/anime/1518/95051.jpg'}),
            call().setInfo(infoLabels={'plot': 'Second Season of the final arc of Gintama.'}, type='video'),
            call('Gintama.: Silver Soul Arc - Second Half War'),
            call().setArt({'icon': 'https://myanimelist.cdn-dena.com/images/anime/1518/95051.jpg'}),
            call().setInfo(infoLabels={'plot': 'Second Season of the final arc of Gintama.'}, type='video'),
            call('Gintama.: Shirogane no Tamashii-hen - Kouhan-sen'),
            call().setArt({'icon': 'https://myanimelist.cdn-dena.com/images/anime/1518/95051.jpg'}),
            call().setInfo(infoLabels={'plot': 'Second Season of the final arc of Gintama.'}, type='video'),
            call('Next Page')
        ])

    def test_successful_retrieval_page_one_with_selected(self):
        handle_val = "Random"
        mock_url = "Random-url"

        mock_plugin = type('', (), {})
        mock_plugin.args = {
            "season": ["Summer"],
            "year": ["2018"],
            "genres": ["Test1,Test2"],
            "page": ["1"]
        }
        mock_plugin.handle = handle_val
        mock_plugin.url_for = Mock(return_value=mock_url)

        mock_route_factory = MagicMock()
        mock_route_factory.get_router_instance = mock_plugin
        sys.modules['resources.lib.router_factory'] = mock_route_factory

        fixture_path = self.dir_path + "/fixtures/animeList/list_success.json"

        with open(fixture_path, "r") as fixture:
            mock_response = fixture.read()

        res_mock = MagicMock()
        res_mock.json = Mock(return_value=json.loads(mock_response))
        self.mock_requests.get = Mock(return_value=res_mock)

        from resources.lib.routes.animelist import anime_list
        anime_list()

        self.mock_requests.get.assert_called_once_with(
            'https://api.animepie.to/Anime/AnimeMain/List',
            params={
                'sort': 1,
                'website': '',
                'genres': 'Test1,Test2',
                'season': 'Summer',
                'limit': 15,
                'year': 2018,
                'sort2': '', 
                'page': 1
            }
        )

        self.mock_xbmc_gui.ListItem.assert_has_calls([
            call('Gintama.: Shirogane no Tamashii-hen 2'),
            call().setArt({'icon': 'https://myanimelist.cdn-dena.com/images/anime/1518/95051.jpg'}),
            call().setInfo(infoLabels={'plot': 'Second Season of the final arc of Gintama.'}, type='video'),
            call('Gintama.: Silver Soul Arc - Second Half War'),
            call().setArt({'icon': 'https://myanimelist.cdn-dena.com/images/anime/1518/95051.jpg'}),
            call().setInfo(infoLabels={'plot': 'Second Season of the final arc of Gintama.'}, type='video'),
            call('Gintama.: Shirogane no Tamashii-hen - Kouhan-sen'),
            call().setArt({'icon': 'https://myanimelist.cdn-dena.com/images/anime/1518/95051.jpg'}),
            call().setInfo(infoLabels={'plot': 'Second Season of the final arc of Gintama.'}, type='video'),
            call('Next Page')
        ])

        # Need to check for order of list items added
        self.mock_xbmc_plugin.addDirectoryItem.assert_has_calls([
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
)

    def test_successful_retrieval_no_next_on_last_page(self):
        handle_val = "Random"
        mock_url = "Random-url"

        mock_plugin = type('', (), {})
        mock_plugin.args = {
            "season": ["Summer"],
            "year": ["2018"],
            "genres": ["Test1,Test2"],
            "page": ["8"]
        }
        mock_plugin.handle = handle_val
        mock_plugin.url_for = Mock(return_value=mock_url)

        mock_route_factory = MagicMock()
        mock_route_factory.get_router_instance = mock_plugin
        sys.modules['resources.lib.router_factory'] = mock_route_factory

        fixture_path = self.dir_path + "/fixtures/animeList/list_success.json"

        with open(fixture_path, "r") as fixture:
            mock_response = fixture.read()

        res_mock = MagicMock()
        res_mock.json = Mock(return_value=json.loads(mock_response))
        self.mock_requests.get = Mock(return_value=res_mock)

        from resources.lib.routes.animelist import anime_list
        anime_list()

        expected_list_item_calls = [
            call('Gintama.: Shirogane no Tamashii-hen 2'),
            call().setArt({'icon': 'https://myanimelist.cdn-dena.com/images/anime/1518/95051.jpg'}),
            call().setInfo(infoLabels={'plot': 'Second Season of the final arc of Gintama.'}, type='video'),
            call('Gintama.: Silver Soul Arc - Second Half War'),
            call().setArt({'icon': 'https://myanimelist.cdn-dena.com/images/anime/1518/95051.jpg'}),
            call().setInfo(infoLabels={'plot': 'Second Season of the final arc of Gintama.'}, type='video'),
            call('Gintama.: Shirogane no Tamashii-hen - Kouhan-sen'),
            call().setArt({'icon': 'https://myanimelist.cdn-dena.com/images/anime/1518/95051.jpg'}),
            call().setInfo(infoLabels={'plot': 'Second Season of the final arc of Gintama.'}, type='video'),
        ]

        self.assertEquals(self.mock_xbmc_gui.ListItem.call_count, 3)
        self.mock_xbmc_gui.ListItem.assert_has_calls(expected_list_item_calls)
        self.mock_requests.get.assert_called_once_with(
            'https://api.animepie.to/Anime/AnimeMain/List',
            params={
                'sort': 1,
                'website': '',
                'genres': 'Test1,Test2',
                'season': 'Summer',
                'limit': 15,
                'year': 2018,
                'sort2': '', 
                'page': 8
            }
        )

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
