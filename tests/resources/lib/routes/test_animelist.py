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
        self.mock_route_factory.get_router_instance = MagicMock()

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
        from resources.lib.routes.animelist import generate_routes, filter_screen, anime_list, year_select, season_select

        mock_plugin = MagicMock()

        generate_routes(mock_plugin)

        mock_plugin.add_route.assert_has_calls([
            call(filter_screen, '/filter'),
            call(anime_list, '/anime-list'),
            call(year_select, '/anime-list/year-select'),
            call(season_select, '/anime-list/season-select'),
        ])

    def test_get_current_params_returns_values_if_passed_in(self):
        from resources.lib.routes.animelist import _get_current_params

        expected_year = "2000"
        expected_season = "Winter"
        expected_page = "Page"

        mock_plugin = type('', (), {})
        mock_plugin.args = {
            "year": [expected_year],
            "season": [expected_season],
            "page": [expected_page],
        }

        args = _get_current_params(mock_plugin)

        self.assertDictEqual(args, {
            "year": expected_year,
            "season": expected_season,
            "page": expected_page
        }, "Returned parameter list does not match plugin.arg values")

    def test_get_current_params_returns_default_values_if_none(self):
        from resources.lib.routes.animelist import _get_current_params

        expected_year = "2018"
        expected_season = "Fall"

        mock_plugin = type('', (), {})
        mock_plugin.args = {}

        args = _get_current_params(mock_plugin)

        self.assertDictEqual(args, {
            "year": expected_year,
            "season": expected_season
        }, "Returned parameter list does not match plugin.arg values")

    def test_should_create_menu_items_with_args_provided(self):
        handle_val = "Random"
        filter_value = { 
            "year": "2018",
            "season": "Winter"
        }

        from resources.lib.routes.animelist import _display_filter_menu_items, anime_list, year_select, season_select

        mock_plugin = type('', (), {})
        mock_plugin.handle = handle_val
        mock_plugin.url_for = MagicMock()

        self.mock_route_factory.get_router_instance.return_value = mock_plugin

        _display_filter_menu_items(mock_plugin, filter_value)

        self.mock_xbmc_gui.ListItem.assert_has_calls([
            call("Year: 2018"),
            call("Season: Winter"),
            call("Search")
        ])

        mock_plugin.url_for.assert_has_calls([
            call(year_select, **filter_value),
            call(season_select, **filter_value),
            call(anime_list, **filter_value)
        ])
        
        self.mock_xbmc_plugin.addDirectoryItem.assert_has_calls(
            map(lambda x: call(handle_val, ANY, ANY, True), range(0, 3))
        )

    def test_should_create_menu_items_with_empty_args(self):
        handle_val = "Random"

        from resources.lib.routes.animelist import _display_filter_menu_items, anime_list, year_select, season_select

        mock_plugin = type('', (), {})
        mock_plugin.handle = handle_val
        mock_plugin.url_for = MagicMock()

        self.mock_route_factory.get_router_instance.return_value = mock_plugin

        _display_filter_menu_items(mock_plugin, {})

        self.mock_xbmc_gui.ListItem.assert_has_calls([
            call("Year: "),
            call("Season: "),
            call("Search")
        ])

        mock_plugin.url_for.assert_has_calls([
            call(year_select),
            call(season_select),
            call(anime_list)
        ])
        
        self.mock_xbmc_plugin.addDirectoryItem.assert_has_calls(
            map(lambda x: call(handle_val, ANY, ANY, True), range(0, 3))
        )

    def common_filter_test(self, updated_filters, plugin_args, methodToTest):
        handle_val = "Random"
        
        filter_values = {
            "year": "2018",
            "season": "Fall"
        }
        filter_values.update(updated_filters)

        from resources.lib.routes.animelist import anime_list, year_select, season_select

        mock_plugin = type('', (), {})
        mock_plugin.args = plugin_args
        mock_plugin.handle = handle_val
        mock_plugin.url_for = MagicMock()

        self.mock_route_factory.get_router_instance.return_value = mock_plugin

        methodToTest()

        mock_plugin.url_for.assert_has_calls([
            call(year_select, **filter_values),
            call(season_select, **filter_values),
            call(anime_list, **filter_values)
        ])

        self.mock_xbmc_gui.ListItem.assert_has_calls([
            call("Year: " + filter_values.get("year")),
            call("Season: " + filter_values.get("season")),
            call("Search")
        ])

        self.mock_xbmc_plugin.endOfDirectory.assert_called_once_with(handle_val)

    def test_year_select_calls_year_select_dialog_and_generates_menu_items(self):
        from resources.lib.routes.animelist import year_select

        passed_filter_values = {
            "year": "2017"
        }

        self.mock_xbmc_gui.Dialog.return_value.select.return_value = 2

        self.common_filter_test(passed_filter_values, {}, year_select)

    def test_year_select_calls_generates_menu_items_based_on_args_if_nothing_selected(self):
        from resources.lib.routes.animelist import year_select

        passed_filter_values = {
            "year": "2009"
        }

        self.mock_xbmc_gui.Dialog.return_value.select.return_value = -1

        plugin_args = {
            "year": [passed_filter_values.get("year")]
        }

        self.common_filter_test(passed_filter_values, plugin_args, year_select)
    
    def test_season_select_calls_season_select_dialog_and_generates_menu_items(self):
        from resources.lib.routes.animelist import season_select

        filter_values = {
            "season": "Spring"
        }

        self.mock_xbmc_gui.Dialog.return_value.select.return_value = 1

        self.common_filter_test(filter_values, {}, season_select)
    
    def test_season_select_calls_season_select_dialog_and_generates_menu_items_with_passed_in_if_none_selected(self):
        from resources.lib.routes.animelist import season_select

        passed_filter_values = {
            "season": "Winter"
        }

        self.mock_xbmc_gui.Dialog.return_value.select.return_value = -1

        plugin_args = {
            "season": [passed_filter_values.get("season")]
        }

        self.common_filter_test(passed_filter_values, plugin_args, season_select)

    def test_filter_screen_generates_filter_menu_items(self):
        from resources.lib.routes.animelist import filter_screen
        self.common_filter_test({}, {}, filter_screen)

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
            "page": "1"
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
            call('Next Page')
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
        mock_plugin.args = {
            "page": "8"
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
