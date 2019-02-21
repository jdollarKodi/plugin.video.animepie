import os
import json
import unittest
from resources.lib.constants.url import BASE_URL, HOME_DETAIL_PATH
from mock import call, patch, MagicMock, ANY

class TestVideoSources(unittest.TestCase):
    def setUp(self):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))

        self.mock_requests = MagicMock()
        
        self.mock_xbmc_addon = MagicMock()
        self.mock_xbmc_addon.getAddonInfo.return_value = "test"

        self.mock_xbmc_plugin = MagicMock()
        self.mock_xbmc_gui = MagicMock()

        self.mock_route_factory = MagicMock()
        self.mock_play_source = MagicMock()

        modules = {
            "requests": self.mock_requests,
            "xbmcadddon": self.mock_xbmc_addon,
            "xbmcgui": self.mock_xbmc_gui,
            "xbmcplugin": self.mock_xbmc_plugin,
            "resources.lib.router_factory": self.mock_route_factory,
            "resources.lib.routes.playsource": self.mock_play_source
        }

        self.module_patcher = patch.dict('sys.modules', modules)
        self.module_patcher.start()

    def tearDown(self):
        self.module_patcher.stop()

    def test_generate_routes(self):
        mock_plugin = MagicMock()

        from resources.lib.routes.videosources import generate_routes, video_sources

        generate_routes(mock_plugin)

        mock_plugin.add_route.assert_has_calls([
            call(video_sources, "/video-sources")
        ])

    def test_video_sources_success(self):
        anime_id = "AnimeID"
        list_id = "ListID"
        episode = "2"

        mock_plugin = type('', (), {})
        mock_plugin.url_for = MagicMock()
        mock_plugin.handle = "Handle"
        mock_plugin.args = {
            "id": [anime_id],
            "listId": [list_id],
            "episode": [episode]
        }

        expected_params = {
            "id": anime_id,
            "listid": list_id,
            "episode": episode
        }

        fixture_path = self.dir_path + "/fixtures/videosources/success.json"

        with open(fixture_path, "r") as fixture:
            mock_response = fixture.read()

        mock_requests_return = MagicMock()
        mock_requests_return.json.return_value = json.loads(mock_response)
        self.mock_requests.get.return_value = mock_requests_return
        self.mock_route_factory.get_router_instance.return_value = mock_plugin

        from resources.lib.routes.videosources import video_sources

        video_sources()

        self.mock_requests.get.assert_called_once_with(BASE_URL + HOME_DETAIL_PATH, params=expected_params)
        mock_requests_return.json.assert_called_once()

        self.mock_xbmc_plugin.addDirectoryItem.assert_has_calls([
            call(mock_plugin.handle, ANY, ANY, True),
            call(mock_plugin.handle, ANY, ANY, True),
            call(mock_plugin.handle, ANY, ANY, True)
        ])

        self.mock_xbmc_gui.ListItem.assert_has_calls([
            call("9A.OpenLoad"),
            call("9A.Streamango"),
            call("GGA.Vidstreaming")
        ])

        mock_plugin.url_for.assert_has_calls([
            call(self.mock_play_source.play_source, source_url='https://openload.co/embed/0Src-Ynealo/', website_name='9A.OpenLoad'),
            call(self.mock_play_source.play_source, source_url='https://streamango.com/embed/nsaddnqafrlcqsea/', website_name='9A.Streamango'),
            call(self.mock_play_source.play_source, source_url='https://vidstreaming.io/streaming.php?id=MTA2NzA4&title=Gintama.%3A+Shirogane+no+Tamashii-hen+2+Episode+3', website_name='GGA.Vidstreaming')
        ])

        self.mock_xbmc_plugin.endOfDirectory.assert_called_once_with(mock_plugin.handle)

