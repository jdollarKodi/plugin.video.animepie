import requests
import math
import logging
import xbmcaddon
import xbmc
from xbmcgui import ListItem, Dialog
from xbmcplugin import addDirectoryItem, endOfDirectory, setResolvedUrl

from resources.lib.router_factory import get_router_instance
from resources.lib.constants.url import BASE_URL, LIST_PATH

ADDON = xbmcaddon.Addon()
logger = logging.getLogger(ADDON.getAddonInfo('id'))

# Genre List: https://api.animepie.to/Anime/Genres
# data: [ 0: {id,name}]

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
PAGE_ARG_KEY = "page"

default_filter_values = {
    YEAR_ARG_KEY: "2018",
    SEASON_ARG_KEY: "Fall"
}

def generate_routes(plugin):
    plugin.add_route(filter_screen, "/filter")
    plugin.add_route(anime_list, "/anime-list")
    # plugin.add_route(genre_select, "/genre-select")
    plugin.add_route(year_select, "/anime-list/year-select")
    plugin.add_route(season_select, "/anime-list/season-select")

    return plugin

def _get_current_params(plugin):
    current_params = {}

    param_keys_with_defaults = [
        YEAR_ARG_KEY,
        SEASON_ARG_KEY
    ]

    for param_key in param_keys_with_defaults:
        if param_key in plugin.args:
            current_params[param_key] = plugin.args[param_key][0]
        else:
            current_params[param_key] = default_filter_values[param_key]

    param_keys_without_defaults = [
        PAGE_ARG_KEY
    ]

    for param_key in param_keys_without_defaults:
        if param_key in plugin.args:
            current_params[param_key] = plugin.args[param_key][0]
    
    return current_params

# def genre_select():
# Genre List: https://api.animepie.to/Anime/Genres
# data: [ 0: {id,name}]
    # logger.debug("Genre Select")
    # plugin = get_router_instance()
    # filter_list_items["year"].setLabel("2")
    # args = { "year": "2000" }
    # args = {}

    # xbmc.executebuiltin("RunPlugin(" + plugin.url_for(filter_screen, **args) + ")")
    # plugin.args = { "year": ["2000"] }
    # plugin.redirect("/filter")
    # plugin.redirect(plugin.url_for(filter_screen, year="2000"))

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


def anime_list():
    plugin = get_router_instance()

    params = {
        "page": "1",
        "limit": "15",
        "year": "2018",
        "season": "Summer",
        "genres": "",
        "sort": "1",
        "sort2": "",
        "website": ""
    }
    params.update(_get_current_params(plugin))

    res = requests.get(BASE_URL + LIST_PATH, params=params)
    json_data = res.json()
    for anime in json_data["data"]["list"]:
        image = anime['backgroundSrc'] if anime['backgroundSrc'] else None
        info = anime['animeSynopsis'] if anime['animeSynopsis'] else ''

        li = ListItem(anime["animeName"])
        li.setArt({'icon': image })
        li.setInfo(type='video', infoLabels={'plot': info})

        addDirectoryItem(
            plugin.handle,
            None,
            # plugin.url_for(
            #     None,
            #     id=anime["animeID"],
            #     listId=anime["animeListID"],
            #     episode_count=anime["animeEpisode"]
            # ),
            li,
            True
        )

    are_pages_remaining = math.ceil(float(json_data["data"]["count"]) / float(params["limit"])) > int(params.get("page"))
    if (are_pages_remaining):
        next_page_params = params
        next_page_params.update({ "page": str(int(params.get("page")) + 1) })

        addDirectoryItem(
            plugin.handle, 
            plugin.url_for(
                anime_list, **next_page_params
            ),
            ListItem('Next Page'),
            True
        )

    endOfDirectory(plugin.handle)
