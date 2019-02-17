import xbmcaddon
from xbmcgui import ListItem
from xbmcplugin import addDirectoryItem, endOfDirectory

def index(plugin):
    ADDON = xbmcaddon.Addon()

    anime_list_str = ADDON.getLocalizedString(32002)
    search_str = ADDON.getLocalizedString(32003)

    addDirectoryItem(plugin.handle, plugin.url_for_path("/anime-list"), ListItem(anime_list_str), True)
    addDirectoryItem(plugin.handle, plugin.url_for_path("/search"), ListItem(search_str), True)
    endOfDirectory(plugin.handle)
