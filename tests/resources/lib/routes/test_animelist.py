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
            "resources.lib.router_factory": self.mock_route_factory
        }

        self.module_patcher = patch.dict('sys.modules', modules)
        self.module_patcher.start()

    def tearDown(self):
        self.module_patcher.stop()

    def test_get_current_params_returns_values_if_passed_in(self):
        from resources.lib.routes.animelist import _get_current_params

        expected_year = "2000"

        mock_plugin = type('', (), {})
        mock_plugin.args = {
            "year": [expected_year]
        }

        args = _get_current_params(mock_plugin)

        self.assertDictEqual(args, {
            "year": expected_year
        }, "Returned parameter list does not match plugin.arg values")

    def test_should_create_menu_items_with_args_provided(self):
        handle_val = "Random"

        from resources.lib.routes.animelist import _display_filter_menu_items, year_select

        mock_route_list = {
            year_select: 'year_select'
        }

        mock_plugin = type('', (), {})
        mock_plugin.handle = handle_val
        mock_plugin.url_for = staticmethod(lambda select: mock_route_list[year_select])

        self.mock_route_factory.get_router_instance.return_value = mock_plugin

        _display_filter_menu_items(mock_plugin, { "year": "2018" })

        self.mock_xbmc_gui.ListItem.assert_has_calls([
            call("Year: 2018"),
            call("Search")
        ])
        
        self.mock_xbmc_plugin.addDirectoryItem.assert_has_calls([
            call(
                handle_val,
                mock_route_list[year_select],
                ANY,
                True
            ),
            call(
                handle_val,
                None,
                ANY,
                True
            ),
        ])

    def test_should_create_menu_items_with_empty_args(self):
        handle_val = "Random"

        from resources.lib.routes.animelist import _display_filter_menu_items, year_select

        mock_route_list = {
            year_select: 'year_select'
        }

        mock_plugin = type('', (), {})
        mock_plugin.handle = handle_val
        mock_plugin.url_for = staticmethod(lambda select: mock_route_list[select])

        self.mock_route_factory.get_router_instance.return_value = mock_plugin

        _display_filter_menu_items(mock_plugin, {})


        expected_list_item_calls = [
            call("Year: "),
            call("Search")
        ]

        self.mock_xbmc_gui.ListItem.assert_has_calls(expected_list_item_calls)

        expected_calls = [
            call(
                handle_val,
                mock_route_list[year_select],
                ANY,
                True
            ),
            call(
                handle_val,
                None,
                ANY,
                True
            ),
        ]
        
        self.mock_xbmc_plugin.addDirectoryItem.assert_has_calls(expected_calls)

    def test_year_select_calls_year_select_and_generates_menu_items(self):
        handle_val = "Random"

        self.mock_xbmc_gui.Dialog.return_value.select.return_value = 1

        from resources.lib.routes.animelist import year_select

        mock_route_list = {
            year_select: 'year_select'
        }

        mock_plugin = type('', (), {})
        mock_plugin.args = {}
        mock_plugin.handle = handle_val
        mock_plugin.url_for = staticmethod(lambda select: mock_route_list[select])

        self.mock_route_factory.get_router_instance.return_value = mock_plugin

        year_select()

        self.mock_xbmc_gui.ListItem.assert_has_calls([
            call("Year: 2018"),
            call("Search")
        ])

        self.mock_xbmc_plugin.addDirectoryItem.assert_has_calls([
            call(
                handle_val,
                mock_route_list[year_select],
                ANY,
                True
            ),
            call(
                handle_val,
                None,
                ANY,
                True
            ),
        ])


# def year_select():
#     logger.debug("Year Select")
#     plugin = get_router_instance()
#     args = _get_current_params(plugin)

#     res = Dialog().select("Choose a year", years)

#     if res >= 0:
#         args[YEAR_ARG_KEY] = years[res]

#     display_filter_menu_items(plugin, args)
#     endOfDirectory(plugin.handle)

# def _display_filter_menu_items(plugin, filter_values):
#     generate_text = lambda label, filter_map, key: label % (filter_map[key] if key in filter_map else '')

#     filter_menu_items = [
#         {
#             "filter_func": year_select,
#             "label": "Year: %s"
#         }
#     ]

#     for menu_item in filter_menu_items:
#         addDirectoryItem(
#             plugin.handle,
#             plugin.url_for(menu_item.get("filter_func")),
#             ListItem(generate_text(menu_item.get("label"), filter_values, YEAR_ARG_KEY)),
#             True
#         )

#     addDirectoryItem(
#         plugin.handle,
#         None,
#         ListItem("Search"),
#         True
#     )

    # def test_successful_retrieval_page_one_none_page(self):
    #     handle_val = "Random"
    #     mock_url = "Random-url"

    #     mock_plugin = type('', (), {})
    #     mock_plugin.args = {}
    #     mock_plugin.handle = handle_val
    #     mock_plugin.url_for = Mock(return_value=mock_url)

    #     mock_route_factory = MagicMock()
    #     mock_route_factory.get_router_instance = mock_plugin
    #     sys.modules['resources.lib.router_factory'] = mock_route_factory

    #     fixture_path = self.dir_path + "/fixtures/animeList/list_success.json"

    #     with open(fixture_path, "r") as fixture:
    #         mock_response = fixture.read()

    #     res_mock = MagicMock()
    #     res_mock.json = Mock(return_value=json.loads(mock_response))
    #     self.mock_requests.get = Mock(return_value=res_mock)

    #     from resources.lib.routes.animelist import anime_list
    #     anime_list()

    #     expected_list_item_calls = [
    #         call('Gintama.: Shirogane no Tamashii-hen 2'),
    #         call().setArt({'icon': 'https://myanimelist.cdn-dena.com/images/anime/1518/95051.jpg'}),
    #         call().setInfo(infoLabels={'plot': 'Second Season of the final arc of Gintama.'}, type='video'),
    #         call('Gintama.: Silver Soul Arc - Second Half War'),
    #         call().setArt({'icon': 'https://myanimelist.cdn-dena.com/images/anime/1518/95051.jpg'}),
    #         call().setInfo(infoLabels={'plot': 'Second Season of the final arc of Gintama.'}, type='video'),
    #         call('Gintama.: Shirogane no Tamashii-hen - Kouhan-sen'),
    #         call().setArt({'icon': 'https://myanimelist.cdn-dena.com/images/anime/1518/95051.jpg'}),
    #         call().setInfo(infoLabels={'plot': 'Second Season of the final arc of Gintama.'}, type='video'),
    #         call('Next Page')
    #     ]

    #     # self.mock_xbmc_gui.ListItem.assert_has_calls(expected_list_item_calls)

    #     # Need to check for order of list items added
    #     expected_calls = [
    #         call(
    #             handle_val,
    #             mock_url,
    #             ANY,
    #             True
    #         ),
    #         call(
    #             handle_val,
    #             mock_url,
    #             ANY,
    #             True
    #         ),
    #         call(
    #             handle_val,
    #             mock_url,
    #             ANY,
    #             True
    #         ),
    #         call(
    #             handle_val,
    #             mock_url,
    #             ANY,
    #             True
    #         ),
    #     ]
        
    #     self.mock_xbmc_plugin.addDirectoryItem.assert_has_calls(expected_calls)

    # def test_successful_retrieval_page_one_with_selected(self):
    #     handle_val = "Random"
    #     mock_url = "Random-url"

    #     mock_plugin = type('', (), {})
    #     mock_plugin.args = {
    #         "page": "1"
    #     }
    #     mock_plugin.handle = handle_val
    #     mock_plugin.url_for = Mock(return_value=mock_url)

    #     mock_route_factory = MagicMock()
    #     mock_route_factory.get_router_instance = mock_plugin
    #     sys.modules['resources.lib.router_factory'] = mock_route_factory

    #     fixture_path = self.dir_path + "/fixtures/animeList/list_success.json"

    #     with open(fixture_path, "r") as fixture:
    #         mock_response = fixture.read()

    #     res_mock = MagicMock()
    #     res_mock.json = Mock(return_value=json.loads(mock_response))
    #     self.mock_requests.get = Mock(return_value=res_mock)

    #     from resources.lib.routes.animelist import anime_list
    #     anime_list()

    #     expected_list_item_calls = [
    #         call('Gintama.: Shirogane no Tamashii-hen 2'),
    #         call().setArt({'icon': 'https://myanimelist.cdn-dena.com/images/anime/1518/95051.jpg'}),
    #         call().setInfo(infoLabels={'plot': 'Second Season of the final arc of Gintama.'}, type='video'),
    #         call('Gintama.: Silver Soul Arc - Second Half War'),
    #         call().setArt({'icon': 'https://myanimelist.cdn-dena.com/images/anime/1518/95051.jpg'}),
    #         call().setInfo(infoLabels={'plot': 'Second Season of the final arc of Gintama.'}, type='video'),
    #         call('Gintama.: Shirogane no Tamashii-hen - Kouhan-sen'),
    #         call().setArt({'icon': 'https://myanimelist.cdn-dena.com/images/anime/1518/95051.jpg'}),
    #         call().setInfo(infoLabels={'plot': 'Second Season of the final arc of Gintama.'}, type='video'),
    #         call('Next Page')
    #     ]

    #     self.mock_xbmc_gui.ListItem.assert_has_calls(expected_list_item_calls)

    #     # Need to check for order of list items added
    #     expected_calls = [
    #         call(
    #             handle_val,
    #             mock_url,
    #             ANY,
    #             True
    #         ),
    #         call(
    #             handle_val,
    #             mock_url,
    #             ANY,
    #             True
    #         ),
    #         call(
    #             handle_val,
    #             mock_url,
    #             ANY,
    #             True
    #         ),
    #         call(
    #             handle_val,
    #             mock_url,
    #             ANY,
    #             True
    #         ),
    #     ]
        
    #     self.mock_xbmc_plugin.addDirectoryItem.assert_has_calls(expected_calls)

    # def test_successful_retrieval_no_next_on_last_page(self):
    #     handle_val = "Random"
    #     mock_url = "Random-url"

    #     mock_plugin = type('', (), {})
    #     mock_plugin.args = {
    #         "page": "8"
    #     }
    #     mock_plugin.handle = handle_val
    #     mock_plugin.url_for = Mock(return_value=mock_url)

    #     mock_route_factory = MagicMock()
    #     mock_route_factory.get_router_instance = mock_plugin
    #     sys.modules['resources.lib.router_factory'] = mock_route_factory

    #     fixture_path = self.dir_path + "/fixtures/animeList/list_success.json"

    #     with open(fixture_path, "r") as fixture:
    #         mock_response = fixture.read()

    #     res_mock = MagicMock()
    #     res_mock.json = Mock(return_value=json.loads(mock_response))
    #     self.mock_requests.get = Mock(return_value=res_mock)

    #     from resources.lib.routes.animelist import anime_list
    #     anime_list()

    #     expected_list_item_calls = [
    #         call('Gintama.: Shirogane no Tamashii-hen 2'),
    #         call().setArt({'icon': 'https://myanimelist.cdn-dena.com/images/anime/1518/95051.jpg'}),
    #         call().setInfo(infoLabels={'plot': 'Second Season of the final arc of Gintama.'}, type='video'),
    #         call('Gintama.: Silver Soul Arc - Second Half War'),
    #         call().setArt({'icon': 'https://myanimelist.cdn-dena.com/images/anime/1518/95051.jpg'}),
    #         call().setInfo(infoLabels={'plot': 'Second Season of the final arc of Gintama.'}, type='video'),
    #         call('Gintama.: Shirogane no Tamashii-hen - Kouhan-sen'),
    #         call().setArt({'icon': 'https://myanimelist.cdn-dena.com/images/anime/1518/95051.jpg'}),
    #         call().setInfo(infoLabels={'plot': 'Second Season of the final arc of Gintama.'}, type='video'),
    #     ]

    #     self.assertEquals(self.mock_xbmc_gui.ListItem.call_count, 3)
    #     self.mock_xbmc_gui.ListItem.assert_has_calls(expected_list_item_calls)

    #     # Need to check for order of list items added
    #     expected_calls = [
    #         call(
    #             handle_val,
    #             mock_url,
    #             ANY,
    #             True
    #         ),
    #         call(
    #             handle_val,
    #             mock_url,
    #             ANY,
    #             True
    #         ),
    #         call(
    #             handle_val,
    #             mock_url,
    #             ANY,
    #             True
    #         ),
    #     ]
        
    #     self.assertEquals(self.mock_xbmc_plugin.addDirectoryItem.call_count, 3)
    #     self.mock_xbmc_plugin.addDirectoryItem.assert_has_calls(expected_calls)
