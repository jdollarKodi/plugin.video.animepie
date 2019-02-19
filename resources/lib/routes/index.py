import xbmcaddon
from xbmcgui import ListItem
from xbmcplugin import addDirectoryItem, endOfDirectory

from resources.lib.router_factory import get_router_instance
from resources.lib.routes.animelist import filter_screen

def generate_routes(main_plugin):
    main_plugin.add_route(index, "/")
    
    return main_plugin

def index():
    ADDON = xbmcaddon.Addon()
    plugin = get_router_instance()

    anime_list_str = ADDON.getLocalizedString(32002)
    search_str = ADDON.getLocalizedString(32003)

    addDirectoryItem(plugin.handle, plugin.url_for(filter_screen), ListItem(anime_list_str), True)
    addDirectoryItem(plugin.handle, plugin.url_for_path("/search"), ListItem(search_str), True)
    endOfDirectory(plugin.handle)
