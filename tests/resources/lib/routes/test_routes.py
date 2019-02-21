import unittest
from mock import call, patch, MagicMock

class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.mock_index = MagicMock()
        self.mock_anime_list = MagicMock()
        self.mock_episode_list = MagicMock()
        self.mock_video_sources = MagicMock()
        self.mock_play_source = MagicMock()
        self.mock_anime_search = MagicMock()

        modules = {
            "resources.lib.routes.index": self.mock_index,
            "resources.lib.routes.animelist": self.mock_anime_list,
            "resources.lib.routes.episodelist": self.mock_episode_list,
            "resources.lib.routes.videosources": self.mock_video_sources,
            "resources.lib.routes.playsource": self.mock_play_source,
            "resources.lib.routes.animesearch": self.mock_anime_search
        }

        self.module_patcher = patch.dict('sys.modules', modules)
        self.module_patcher.start()

    def tearDown(self):
        self.module_patcher.stop()

    def test_route_generation(self):
        from resources.lib.routes.routes import generate_all_routes

        mock_plugin = "test"

        generate_all_routes(mock_plugin)

        route_mocks = [
            self.mock_index,
            self.mock_anime_list,
            self.mock_episode_list,
            self.mock_video_sources,
            self.mock_play_source,
            self.mock_anime_search
        ]

        for route_mock in route_mocks:
            route_mock.generate_routes.assert_called_once_with(mock_plugin)
