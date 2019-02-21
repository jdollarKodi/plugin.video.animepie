import unittest
from mock import call, patch, MagicMock

class TestAnimeSearch(unittest.TestCase):
    def setUp(self):
        self.mock_xbmc_gui = MagicMock()
        self.mock_xbmc_plugin = MagicMock()

        self.mock_xbmc_addon_inst = MagicMock()
        self.mock_xbmc_addon_inst.getAddonInfo.return_value = "Addon ID"
        self.mock_xbmc_addon = MagicMock()
        self.mock_xbmc_addon.Addon.return_value = self.mock_xbmc_addon_inst

        self.mock_route_factory = MagicMock()

        modules = {
            "xbmcplugin": self.mock_xbmc_plugin,
            "xbmcgui": self.mock_xbmc_gui,
            "xbmcaddon": self.mock_xbmc_addon,
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

    def test_search_success(self):
        mock_plugin = type('', (), {})
        mock_plugin.handle = "Test"

        self.mock_route_factory.get_router_instance.return_value = mock_plugin

        from resources.lib.routes.animesearch import anime_search

        anime_search()

        self.mock_xbmc_plugin.endOfDirectory.assert_called_once_with(mock_plugin.handle)
