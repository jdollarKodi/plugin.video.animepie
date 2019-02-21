import logging
import xbmcaddon
from xbmcgui import ListItem
from xbmcplugin import addDirectoryItem, endOfDirectory
from resources.lib.router_factory import get_router_instance

ADDON = xbmcaddon.Addon()
logger = logging.getLogger(ADDON.getAddonInfo('id'))

def generate_routes(plugin):
    plugin.add_route(anime_search, "/search")

    return plugin

def anime_search():
    plugin = get_router_instance()

    endOfDirectory(plugin.handle)
