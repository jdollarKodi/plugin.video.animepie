import unittest
from mock import call, patch, MagicMock, ANY

class TestPlaySource(unittest.TestCase):
    def setUp(self):
        self.mock_xbmc = MagicMock()
        self.mock_xbmc_plugin = MagicMock()
        self.mock_xbmc_gui = MagicMock()

        self.mock_addon_inst = MagicMock()
        self.mock_addon_inst.getAddonInfo.return_value = ''
        self.mock_xbmc_addon = MagicMock()
        self.mock_xbmc_addon.Addon.return_value = self.mock_addon_inst

        self.mock_requests = MagicMock()
        self.mock_requests_inst = MagicMock()
        self.mock_requests.get.return_value = self.mock_requests_inst

        self.mock_bs4 = MagicMock()
        self.mock_resolve_url = MagicMock()
        self.embed_processors = MagicMock()

        self.mock_plugin = type('', (), {})
        self.mock_route_factory = MagicMock()
        self.mock_route_factory.get_router_instance.return_value = self.mock_plugin

        modules = {
            "xbmc": self.mock_xbmc,
            "xbmcplugin": self.mock_xbmc_plugin,
            "xbmcgui": self.mock_xbmc_gui,
            "xbmcaddon": self.mock_xbmc_addon,
            "requests": self.mock_requests,
            "resolveurl": self.mock_resolve_url,
            "bs4": self.mock_bs4,
            "resources.lib.router_factory": self.mock_route_factory,
            "resources.lib.embed_processors": self.embed_processors
        }

        self.module_patcher = patch.dict('sys.modules', modules)
        self.module_patcher.start()

    def tearDown(self):
        self.module_patcher.stop()

    def reset_mocks(self):
        self.mock_xbmc.reset_mock()
        self.mock_xbmc_plugin.reset_mock()
        self.mock_xbmc_gui.reset_mock()

        self.mock_addon_inst.reset_mock()
        self.mock_xbmc_addon.reset_mock()
        self.mock_addon_inst.getAddonInfo.return_value = ''
        self.mock_xbmc_addon.Addon.return_value = self.mock_addon_inst

        self.mock_requests.reset_mock()
        self.mock_requests_inst.reset_mock()
        self.mock_requests.get.return_value = self.mock_requests_inst

        self.mock_bs4.reset_mock()
        self.mock_resolve_url.reset_mock()
        self.embed_processors.reset_mock()

        self.mock_plugin = type('', (), {})
        self.mock_route_factory.reset_mock()
        self.mock_route_factory.get_router_instance.return_value = self.mock_plugin
    
    def test_generate_routes(self):
        from resources.lib.routes.playsource import generate_routes, play_source

        mock_plugin = MagicMock()
        generate_routes(mock_plugin)

        mock_plugin.add_route.assert_has_calls([
            call(play_source, "/video-source/play")
        ])

    def test_playsource_custom_processor_success(self):
        source_url = "http://fake.com"
        expected_source_url = "http://processed.com"

        processors = [
            { 
                "website_name": "TEST.MP4UPLOAD",
                "retrieve_func": self.embed_processors.mp4upload.retrieve_source_url,
            },
            { 
                "website_name": "TEST.Streamango",
                "retrieve_func": self.embed_processors.streamango.retrieve_source_url,
            },
        ]

        for processor in processors:
            self.mock_plugin.args = {
                "website_name": [processor.get("website_name")],
                "source_url": [source_url],
            }

            mock_player = MagicMock()
            self.mock_xbmc.Player.return_value = mock_player

            processor.get("retrieve_func").return_value = (None, expected_source_url)

            from resources.lib.routes.playsource import play_source

            play_source()

            self.mock_requests.get.assert_called_once_with(source_url)
            self.mock_bs4.BeautifulSoup.assert_called_once_with(ANY, 'html.parser')
            processor.get("retrieve_func").assert_called_once()
            self.mock_xbmc_gui.ListItem.assert_called_once_with(path=expected_source_url)
            mock_player.play.assert_called_once_with(expected_source_url, ANY)

            self.reset_mocks()
            mock_player.reset_mock()

    # def test_playsource_custom_processor_error(self):

    # def test_playsource_resolveurl_success(self):

    # def test_playsource_resolveurl_no_url(self):

    # def test_playsource_resolveurl_exception(self):
