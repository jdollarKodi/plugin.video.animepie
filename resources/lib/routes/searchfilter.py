import logging
import xbmcaddon
from xbmcgui import ListItem, Dialog
from xbmcplugin import addDirectoryItem, endOfDirectory
from resources.lib.router_factory import get_router_instance
from resources.lib.routes.animesearch import anime_search

ADDON = xbmcaddon.Addon()
logger = logging.getLogger(ADDON.getAddonInfo('id'))

NAME_ARG_KEY = "name"

def generate_routes(plugin):
    plugin.add_route(search_filter, "/search/filter")
    plugin.add_route(name_filter, "/search/filter/name")
    return plugin

def _display_filter_menu_items(plugin, filter_values):
    generate_text = lambda label, filter_map, key: label % (filter_map[key] if key in filter_map else '')

    filter_menu_items = [
        {
            "filter_func": name_filter,
            "label": "Name: %s",
            "key": NAME_ARG_KEY
        },
    ]

    for menu_item in filter_menu_items:
        addDirectoryItem(
            plugin.handle,
            plugin.url_for(menu_item.get("filter_func"), **filter_values),
            ListItem(generate_text(menu_item.get("label"), filter_values, menu_item.get("key"))),
            True
        )

    addDirectoryItem(
        plugin.handle,
        plugin.url_for(anime_search, **filter_values),
        ListItem("Search"),
        True
    )

def name_filter():
    plugin = get_router_instance()

    name_input = Dialog().input("Enter anime name")
    _display_filter_menu_items(plugin, { "name": name_input })

    endOfDirectory(plugin.handle)

def search_filter():
    plugin = get_router_instance()

    _display_filter_menu_items(plugin, { "name": "" })

    endOfDirectory(plugin.handle)
