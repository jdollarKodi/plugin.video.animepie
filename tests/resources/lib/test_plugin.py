import unittest
from mock import call, patch, MagicMock

class TestPlugin(unittest.TestCase):
    def setUp(self):
        mock_xbmc_addon_inst = MagicMock()
        mock_xbmc_addon_inst.getAddonInfo.return_value = "id"
        self.mock_xbmc_addon = MagicMock()
        self.mock_xbmc_addon.Addon.return_value = mock_xbmc_addon_inst

        self.mock_lib = MagicMock()
        self.mock_routes = MagicMock()
        self.mock_router_factory = MagicMock()

        modules = {
            "logging": MagicMock(),
            "xbmcaddon": self.mock_xbmc_addon,
            "resources.lib.routes.routes": self.mock_routes,
            "resources.lib.router_factory": self.mock_router_factory
        }

        self.module_patcher = patch.dict('sys.modules', modules)
        self.module_patcher.start()

    def tearDown(self):
        self.module_patcher.stop()

    def test_run(self):
        mock_plugin = MagicMock()

        self.mock_router_factory.get_router_instance.return_value = mock_plugin

        from resources.lib import plugin
        plugin.run()

        self.mock_routes.generate_all_routes.assert_called_once_with(mock_plugin)
        mock_plugin.run.assert_called_once()
