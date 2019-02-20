import unittest
from mock import call, patch, MagicMock, Mock, ANY

class TestRouterFactory(unittest.TestCase):
    def setUp(self):
        self.mock_routing = MagicMock()
        modules = {
            "routing": self.mock_routing,
        }

        self.module_patcher = patch.dict('sys.modules', modules)
        self.module_patcher.start()

    def tearDown(self):
        self.module_patcher.stop()

    def test_retrieves_router_instance_if_none_defined(self):
        from resources.lib.router_factory import get_router_instance

        expected_instance = 'test'
        self.mock_routing.Plugin.return_value = expected_instance

        router_instance = get_router_instance()

        self.assertEqual(router_instance, expected_instance)
        self.mock_routing.Plugin.assert_called_once()

    def test_returns_originally_defined_router_instance(self):
        from resources.lib.router_factory import get_router_instance

        expected_instance = 'test'
        self.mock_routing.Plugin.return_value = expected_instance

        router_instance = get_router_instance()
        router_instance2 = get_router_instance()

        self.assertEqual(router_instance, expected_instance)
        self.assertEqual(router_instance2, expected_instance)
        self.mock_routing.Plugin.assert_called_once()
