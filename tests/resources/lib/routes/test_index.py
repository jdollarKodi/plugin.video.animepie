import sys
import unittest
from mock import call, patch, MagicMock, Mock, ANY

class TestIndex(unittest.TestCase):
  def setUp(self):
      mock_xbmc_gui = MagicMock()
      mock_xbmc_gui.ListItem = MagicMock()
      self.mock_xbmc_gui = mock_xbmc_gui

      mock_xbmc_plugin = MagicMock()
      mock_xbmc_plugin.addDirectoryItem = MagicMock()
      self.mock_xbmc_plugin = mock_xbmc_plugin

      mock_xbmc_addon_inst = MagicMock()
      mock_xbmc_addon_inst.getLocalizedString = MagicMock()
      mock_xbmc_addon_inst.getAddonInfo.return_value = "test"
      mock_xbmc_addon = MagicMock()
      mock_xbmc_addon.Addon.return_value = mock_xbmc_addon_inst
      self.mock_xbmc_addon = mock_xbmc_addon
      self.mock_xbmc_addon_inst = mock_xbmc_addon_inst

      modules = {
        'resolveurl': MagicMock(),
        'xbmcaddon': self.mock_xbmc_addon,
        'xbmcgui': self.mock_xbmc_gui,
        'xbmcplugin': self.mock_xbmc_plugin
      }

      self.module_patcher = patch.dict('sys.modules', modules)
      self.module_patcher.start()
  
  def tearDown(self):
    self.module_patcher.stop()

  def test_directory_generation(self):
    handle_val = "Random"

    mock_plugin = type('', (), {})
    mock_plugin.handle = handle_val
    mock_plugin.url_for = MagicMock()
    mock_plugin.url_for_path = MagicMock()

    mock_route_factory = MagicMock()
    mock_route_factory.get_router_instance = mock_plugin
    sys.modules['resources.lib.router_factory'] = mock_route_factory

    from resources.lib.routes.index import index
    index()

    # The call to listItems is a little weird
    calls_to_addDirectoryItem = [
        call(
            handle_val,
            ANY,
            ANY,
            True
        ),
        call(
            handle_val,
            ANY,
            ANY,
            True
        )
    ]

    self.mock_xbmc_addon_inst.getLocalizedString.assert_has_calls([
      call(32002),
      call(32003)
    ])
    self.mock_xbmc_plugin.addDirectoryItem.assert_has_calls(calls_to_addDirectoryItem)
    self.mock_xbmc_plugin.endOfDirectory.assert_called_once_with(handle_val)
