
import sys
import os
import json
import unittest
from mock import call, patch, MagicMock, Mock, ANY

class TestListFilter(unittest.TestCase):
    def setUp(self):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))

        self.mock_requests = MagicMock()

        self.mock_xbmc_plugin = MagicMock()
        self.mock_xbmc_gui = MagicMock()

        self.mock_route_factory = MagicMock()
        self.mock_anime_list = MagicMock()

        modules = {
            "requests": self.mock_requests,
            "xbmcplugin": self.mock_xbmc_plugin,
            "xbmcgui": self.mock_xbmc_gui,
            "xbmcadddon": MagicMock(),
            "resolveurl": MagicMock(),
            "resources.lib.routes.animelist": self.mock_anime_list,
            "resources.lib.router_factory": self.mock_route_factory
        }

        self.module_patcher = patch.dict('sys.modules', modules)
        self.module_patcher.start()

    def tearDown(self):
        self.module_patcher.stop()

    def test_generate_routes(self):
        from resources.lib.routes.listfilter import generate_routes, filter_screen, year_select, season_select, genre_select

        mock_plugin = MagicMock()

        generate_routes(mock_plugin)

        mock_plugin.add_route.assert_has_calls([
            call(filter_screen, '/filter'),
            call(year_select, '/anime-list/year-select'),
            call(season_select, '/anime-list/season-select'),
            call(genre_select, '/anime-list/genre-select')
        ])

    def test_get_current_params_returns_values_if_passed_in(self):
        from resources.lib.routes.listfilter import _get_current_params

        expected_year = "2000"
        expected_season = "Winter"
        expected_genre = "Test,Test2"
        expected_page = "Page"

        mock_plugin = type('', (), {})
        mock_plugin.args = {
            "year": [expected_year],
            "season": [expected_season],
            "genres": [expected_genre],
        }

        args = _get_current_params(mock_plugin)

        self.assertDictEqual(args, {
            "year": expected_year,
            "season": expected_season,
            "genres": expected_genre,
        }, "Returned parameter list does not match plugin.arg values")

    def test_get_current_params_returns_default_values_if_none(self):
        from resources.lib.routes.listfilter import _get_current_params

        expected_year = "2018"
        expected_season = "Fall"
        expected_genre = ""

        mock_plugin = type('', (), {})
        mock_plugin.args = {}

        args = _get_current_params(mock_plugin)

        self.assertDictEqual(args, {
            "year": expected_year,
            "season": expected_season,
            "genres": expected_genre
        }, "Returned parameter list does not match plugin.arg values")

    def test_should_create_menu_items_with_args_provided(self):
        handle_val = "Random"
        filter_value = { 
            "year": "2018",
            "season": "Winter",
            "genres": "Test,Test2",
        }

        from resources.lib.routes.listfilter import _display_filter_menu_items, year_select, season_select, genre_select

        mock_plugin = type('', (), {})
        mock_plugin.handle = handle_val
        mock_plugin.url_for = MagicMock()

        self.mock_route_factory.get_router_instance.return_value = mock_plugin

        _display_filter_menu_items(mock_plugin, filter_value)

        self.mock_xbmc_gui.ListItem.assert_has_calls([
            call("Year: 2018"),
            call("Season: Winter"),
            call("Genres: Test,Test2"),
            call("Search")
        ])

        mock_plugin.url_for.assert_has_calls([
            call(year_select, **filter_value),
            call(season_select, **filter_value),
            call(genre_select, **filter_value),
            call(self.mock_anime_list.anime_list, **filter_value)
        ])
        
        self.mock_xbmc_plugin.addDirectoryItem.assert_has_calls(
            map(lambda x: call(handle_val, ANY, ANY, True), range(0, 3))
        )

    def test_should_create_menu_items_with_empty_args(self):
        handle_val = "Random"

        from resources.lib.routes.listfilter import _display_filter_menu_items, year_select, season_select, genre_select

        mock_plugin = type('', (), {})
        mock_plugin.handle = handle_val
        mock_plugin.url_for = MagicMock()

        self.mock_route_factory.get_router_instance.return_value = mock_plugin

        _display_filter_menu_items(mock_plugin, {})

        self.mock_xbmc_gui.ListItem.assert_has_calls([
            call("Year: "),
            call("Season: "),
            call("Genres: "),
            call("Search")
        ])

        mock_plugin.url_for.assert_has_calls([
            call(year_select),
            call(season_select),
            call(genre_select),
            call(self.mock_anime_list.anime_list)
        ])
        
        self.mock_xbmc_plugin.addDirectoryItem.assert_has_calls(
            map(lambda x: call(handle_val, ANY, ANY, True), range(0, 3))
        )

    def common_filter_test(self, updated_filters, plugin_args, methodToTest):
        handle_val = "Random"
        
        filter_values = {
            "year": "2018",
            "season": "Fall",
            "genres": "",
        }
        filter_values.update(updated_filters)

        from resources.lib.routes.listfilter import year_select, season_select, genre_select

        mock_plugin = type('', (), {})
        mock_plugin.args = plugin_args
        mock_plugin.handle = handle_val
        mock_plugin.url_for = MagicMock()

        self.mock_route_factory.get_router_instance.return_value = mock_plugin

        methodToTest()

        mock_plugin.url_for.assert_has_calls([
            call(year_select, **filter_values),
            call(season_select, **filter_values),
            call(genre_select, **filter_values),
            call(self.mock_anime_list.anime_list, **filter_values)
        ])

        self.mock_xbmc_gui.ListItem.assert_has_calls([
            call("Year: " + filter_values.get("year")),
            call("Season: " + filter_values.get("season")),
            call("Genres: " + filter_values.get("genres")),
            call("Search")
        ])

        self.mock_xbmc_plugin.endOfDirectory.assert_called_once_with(handle_val)

    def test_year_select_calls_year_select_dialog_and_generates_menu_items(self):
        from resources.lib.routes.listfilter import year_select

        passed_filter_values = {
            "year": "2017"
        }

        self.mock_xbmc_gui.Dialog.return_value.select.return_value = 2

        self.common_filter_test(passed_filter_values, {}, year_select)

    def test_year_select_calls_generates_menu_items_based_on_args_if_nothing_selected(self):
        from resources.lib.routes.listfilter import year_select

        passed_filter_values = {
            "year": "2009"
        }

        self.mock_xbmc_gui.Dialog.return_value.select.return_value = -1

        plugin_args = {
            "year": [passed_filter_values.get("year")]
        }

        self.common_filter_test(passed_filter_values, plugin_args, year_select)
    
    def test_season_select_calls_season_select_dialog_and_generates_menu_items(self):
        from resources.lib.routes.listfilter import season_select

        filter_values = {
            "season": "Spring"
        }

        self.mock_xbmc_gui.Dialog.return_value.select.return_value = 1

        self.common_filter_test(filter_values, {}, season_select)
    
    def test_season_select_calls_season_select_dialog_and_generates_menu_items_with_passed_in_if_none_selected(self):
        from resources.lib.routes.listfilter import season_select

        passed_filter_values = {
            "season": "Winter"
        }

        self.mock_xbmc_gui.Dialog.return_value.select.return_value = -1

        plugin_args = {
            "season": [passed_filter_values.get("season")]
        }

        self.common_filter_test(passed_filter_values, plugin_args, season_select)

    def test_genre_select_calls_multiselect_and_generates_menu_items_if_none_selected(self):
        fixture_path = self.dir_path + "/fixtures/animeList/genre_success.json"

        with open(fixture_path, "r") as fixture:
            mock_response = fixture.read()

        self.mock_requests.get.return_value.json.return_value = json.loads(mock_response)

        from resources.lib.routes.listfilter import genre_select

        passed_filter_values = {
            "genres": ""
        }

        plugin_args = {
            "genres": ["Test,Test2"]
        }

        mock_dialog_inst = MagicMock()
        mock_dialog_inst.multiselect.return_value = None
        self.mock_xbmc_gui.Dialog.return_value = mock_dialog_inst

        self.common_filter_test(passed_filter_values, plugin_args, genre_select)
        mock_dialog_inst.multiselect.assert_called_once_with("Select Genres", ["Action", "Adventure", "Cars"])

    def test_genre_select_calls_multiselect_and_generates_menu_items_if_single_selected(self):
        fixture_path = self.dir_path + "/fixtures/animeList/genre_success.json"

        with open(fixture_path, "r") as fixture:
            mock_response = fixture.read()

        self.mock_requests.get.return_value.json.return_value = json.loads(mock_response)

        from resources.lib.routes.listfilter import genre_select

        passed_filter_values = {
            "genres": "Adventure"
        }

        plugin_args = {
            "genres": ["Test"]
        }

        mock_dialog_inst = MagicMock()
        mock_dialog_inst.multiselect.return_value = [1]
        self.mock_xbmc_gui.Dialog.return_value = mock_dialog_inst

        genre_list = ["Action", "Adventure", "Cars"]

        self.common_filter_test(passed_filter_values, plugin_args, genre_select)
        mock_dialog_inst.multiselect.assert_called_once_with("Select Genres", genre_list)

    def test_genre_select_calls_multiselect_and_generates_menu_items_if_multiple_selected(self):
        fixture_path = self.dir_path + "/fixtures/animeList/genre_success.json"

        with open(fixture_path, "r") as fixture:
            mock_response = fixture.read()

        self.mock_requests.get.return_value.json.return_value = json.loads(mock_response)

        from resources.lib.routes.listfilter import genre_select

        passed_filter_values = {
            "genres": "Action,Adventure"
        }

        plugin_args = {
            "genres": ["Test"]
        }

        mock_dialog_inst = MagicMock()
        mock_dialog_inst.multiselect.return_value = [0, 1]
        self.mock_xbmc_gui.Dialog.return_value = mock_dialog_inst

        genre_list = ["Action", "Adventure", "Cars"]

        self.common_filter_test(passed_filter_values, plugin_args, genre_select)
        mock_dialog_inst.multiselect.assert_called_once_with("Select Genres", genre_list)

    def test_filter_screen_generates_filter_menu_items(self):
        from resources.lib.routes.listfilter import filter_screen
        self.common_filter_test({}, {}, filter_screen)
