import unittest
from mock import call, patch, MagicMock, ANY

class TestEpisodeList(unittest.TestCase):
    def setUp(self):
        self.mock_xbmc_plugin = MagicMock()
        self.mock_xbmc_gui = MagicMock()

        self.mock_addon_inst = MagicMock()
        self.mock_addon_inst.getAddonInfo.return_value = ''
        self.mock_xbmc_addon = MagicMock()
        self.mock_xbmc_addon.Addon.return_value = self.mock_addon_inst

        self.mock_route_factory = MagicMock()
        self.mock_video_source = MagicMock()

        modules = {
            "xbmcplugin": self.mock_xbmc_plugin,
            "xbmcgui": self.mock_xbmc_gui,
            "xbmcaddon": self.mock_xbmc_addon,
            "resolveurl": MagicMock(),
            "resources.lib.router_factory": self.mock_route_factory,
            "resources.lib.routes.videosources": self.mock_video_source
        }

        self.module_patcher = patch.dict('sys.modules', modules)
        self.module_patcher.start()

    def tearDown(self):
        self.module_patcher.stop()
    
    def test_generate_routes(self):
        from resources.lib.routes.episodelist import generate_routes, episode_list

        mock_plugin = MagicMock()
        generate_routes(mock_plugin)

        mock_plugin.add_route.assert_has_calls([
            call(episode_list, "/episode-list")
        ])

    def test_episode_list_generates_list_based_on_episode_count(self):
        arg_id = "test_id"
        list_id = "test_list_id"
        episode_count = 3

        mock_plugin = type('', (), {})
        mock_plugin.handle = 'test'
        mock_plugin.args = {
            "id": [arg_id],
            "listId": [list_id],
            "episode_count": [episode_count]
        }
        mock_plugin.url_for = MagicMock()

        self.mock_route_factory.get_router_instance.return_value = mock_plugin

        self.mock_addon_inst.getLocalizedString.return_value = "test %s"

        from resources.lib.routes.episodelist import episode_list

        episode_list()

        self.mock_xbmc_gui.ListItem.assert_has_calls([
            call("test 1"),
            call("test 2"),
            call("test 3"),
        ])

        expected_url_for_args = {
            "id": arg_id,
            "listId": list_id,
        }

        mock_plugin.url_for.assert_has_calls([
            call(self.mock_video_source.video_sources, episode='1', **expected_url_for_args),
            call(self.mock_video_source.video_sources, episode='2', **expected_url_for_args),
            call(self.mock_video_source.video_sources, episode='3', **expected_url_for_args),
        ])

        self.mock_xbmc_plugin.addDirectoryItem.assert_has_calls([
            call(mock_plugin.handle, ANY, ANY, True),
            call(mock_plugin.handle, ANY, ANY, True),
            call(mock_plugin.handle, ANY, ANY, True)
        ])

        self.mock_xbmc_plugin.endOfDirectory(mock_plugin.handle)
