import unittest
from mock import call, patch, MagicMock

class TestSearchFilter(unittest.TestCase):
    def setUp(self):
        self.mock_xbmc_gui = MagicMock()
        self.mock_xbmc_plugin = MagicMock()

        self.mock_xbmc_addon_inst = MagicMock()
        self.mock_xbmc_addon_inst.getAddonInfo.return_value = "Addon ID"
        self.mock_xbmc_addon = MagicMock()
        self.mock_xbmc_addon.Addon.return_value = self.mock_xbmc_addon_inst

        self.mock_route_factory = MagicMock()
        self.mock_anime_search = MagicMock()

        modules = {
            'xbmcgui': self.mock_xbmc_gui,
            'xbmcplugin': self.mock_xbmc_plugin,
            'xbmcaddon': self.mock_xbmc_addon,
            'resources.lib.router_factory': self.mock_route_factory,
            'resources.lib.routes.animesearch': self.mock_anime_search
        }

        self.module_patcher = patch.dict('sys.modules', modules)
        self.module_patcher.start()

    def tearDown(self):
        self.module_patcher.stop()

    def common_filter_test(self, updated_filters, plugin_args, methodToTest):
        handle_val = "Random"
        
        filter_values = {
            "name": "",
        }
        filter_values.update(updated_filters)

        from resources.lib.routes.searchfilter import name_filter

        mock_plugin = type('', (), {})
        mock_plugin.args = plugin_args
        mock_plugin.handle = handle_val
        mock_plugin.url_for = MagicMock()

        self.mock_route_factory.get_router_instance.return_value = mock_plugin

        methodToTest()

        mock_plugin.url_for.assert_has_calls([
            call(name_filter, **filter_values),
            call(self.mock_anime_search.anime_search, **filter_values)
        ])

        self.mock_xbmc_gui.ListItem.assert_has_calls([
            call("Name: " + filter_values.get("name")),
            call("Search")
        ])

        self.mock_xbmc_plugin.endOfDirectory.assert_called_once_with(handle_val)

    def test_generate_routes(self):
        mock_plugin = MagicMock()
        
        from resources.lib.routes.searchfilter import generate_routes, search_filter, name_filter

        generate_routes(mock_plugin)

        mock_plugin.add_route.assert_has_calls([
            call(search_filter, "/search/filter"),
            call(name_filter, "/search/filter/name")
        ])

    def test_search_filter(self):
        from resources.lib.routes.searchfilter import search_filter
        self.common_filter_test({ }, {}, search_filter)

    def test_name_filter(self):
        self.mock_xbmc_gui.Dialog.return_value.input.return_value = "test"

        from resources.lib.routes.searchfilter import name_filter
        self.common_filter_test({ "name": "test" }, {}, name_filter)
