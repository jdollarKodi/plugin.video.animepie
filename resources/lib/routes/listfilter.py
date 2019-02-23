import requests
import logging
import xbmcaddon
import xbmc
from xbmcgui import ListItem, Dialog
from xbmcplugin import addDirectoryItem, endOfDirectory

from resources.lib.router_factory import get_router_instance
from resources.lib.constants.url import BASE_URL, GENRE_PATH
from resources.lib.routes.animelist import anime_list

ADDON = xbmcaddon.Addon()
logger = logging.getLogger(ADDON.getAddonInfo('id'))

years = [
    "ALL", # Nothing passed for year param
    "2018",
    "2017",
    "2016",
    "2015",
    "2014",
    "2013",
    "2012",
    "2011",
    "2010",
    "2009",
    "2008",
    "2007",
    "2006",
    "2005"
]

seasons = [
    "Winter",
    "Spring",
    "Summer",
    "Fall"
]

YEAR_ARG_KEY = "year"
SEASON_ARG_KEY = "season"
GENRES_ARG_KEY = "genres"

default_filter_values = {
    YEAR_ARG_KEY: "2018",
    SEASON_ARG_KEY: "Fall",
    GENRES_ARG_KEY: "",
}

def generate_routes(plugin):
    plugin.add_route(filter_screen, "/filter")
    plugin.add_route(year_select, "/anime-list/year-select")
    plugin.add_route(season_select, "/anime-list/season-select")
    plugin.add_route(genre_select, "/anime-list/genre-select")

    return plugin

def _get_current_params(plugin):
    current_params = {}

    param_keys_with_defaults = [
        YEAR_ARG_KEY,
        SEASON_ARG_KEY,
        GENRES_ARG_KEY
    ]

    for param_key in param_keys_with_defaults:
        if param_key in plugin.args:
            current_params[param_key] = plugin.args[param_key][0]
        else:
            current_params[param_key] = default_filter_values[param_key]

    return current_params

def _display_filter_menu_items(plugin, filter_values):
    generate_text = lambda label, filter_map, key: label % (filter_map[key] if key in filter_map else '')

    filter_menu_items = [
        {
            "filter_func": year_select,
            "label": "Year: %s",
            "key": YEAR_ARG_KEY
        },
        {
            "filter_func": season_select,
            "label": "Season: %s",
            "key": SEASON_ARG_KEY
        },
        {
            "filter_func": genre_select,
            "label": "Genres: %s",
            "key": GENRES_ARG_KEY
        }
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
        plugin.url_for(anime_list, **filter_values),
        ListItem("Search"),
        True
    )

def genre_select():
    logger.debug("Genre select")
    plugin = get_router_instance()
    args = _get_current_params(plugin)

    res = requests.get(BASE_URL + GENRE_PATH)
    json_data = res.json()

    list_of_genres = list(map(lambda genre_obj: genre_obj.get("name"), json_data.get("data")))

    res = Dialog().multiselect("Select Genres", list_of_genres)

    if res == None:
        args[GENRES_ARG_KEY] = ""
    else:
        args[GENRES_ARG_KEY] = ",".join(list(map(lambda i: list_of_genres[i], res)))

    _display_filter_menu_items(plugin, args)
    endOfDirectory(plugin.handle)

def year_select():
    logger.debug("Year select")
    plugin = get_router_instance()
    args = _get_current_params(plugin)

    res = Dialog().select("Choose a year", years)

    if res >= 0:
        args[YEAR_ARG_KEY] = years[res]

    _display_filter_menu_items(plugin, args)
    endOfDirectory(plugin.handle)

def season_select():
    logger.debug("Season select")
    plugin = get_router_instance()
    args = _get_current_params(plugin)

    res = Dialog().select("Choose a season", seasons)

    if res >= 0:
        args[SEASON_ARG_KEY] = seasons[res]

    _display_filter_menu_items(plugin, args)
    endOfDirectory(plugin.handle)

def filter_screen():
    logger.debug("Inside filter screen")
    plugin = get_router_instance()

    _display_filter_menu_items(plugin, _get_current_params(plugin))

    endOfDirectory(plugin.handle)
