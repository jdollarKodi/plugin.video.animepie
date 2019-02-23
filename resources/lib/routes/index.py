import xbmcaddon
from xbmcgui import ListItem
from xbmcplugin import addDirectoryItem, endOfDirectory

from resources.lib.router_factory import get_router_instance
from resources.lib.routes.listfilter import filter_screen
from resources.lib.routes.searchfilter import search_filter

def generate_routes(main_plugin):
    main_plugin.add_route(index, "/")
    
    return main_plugin

def index():
    ADDON = xbmcaddon.Addon()
    plugin = get_router_instance()

    anime_list_str = ADDON.getLocalizedString(32002)
    search_str = ADDON.getLocalizedString(32003)

    addDirectoryItem(plugin.handle, plugin.url_for(filter_screen), ListItem(anime_list_str), True)
    addDirectoryItem(plugin.handle, plugin.url_for(search_filter), ListItem(search_str), True)
    endOfDirectory(plugin.handle)
