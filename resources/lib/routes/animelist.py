import requests
import math
import logging
import xbmcaddon
import xbmc
from xbmcgui import ListItem
from xbmcplugin import addDirectoryItem, endOfDirectory

from resources.lib.router_factory import get_router_instance
from resources.lib.constants.url import BASE_URL, LIST_PATH
from resources.lib.routes.episodelist import episode_list

ADDON = xbmcaddon.Addon()
logger = logging.getLogger(ADDON.getAddonInfo('id'))

YEAR_ARG_KEY = "year"
SEASON_ARG_KEY = "season"
GENRES_ARG_KEY = "genres"
PAGE_ARG_KEY = "page"

def generate_routes(plugin):
    plugin.add_route(anime_list, "/anime-list")

    return plugin

def _get_current_params(plugin):
    current_params = {}

    param_keys = [
        YEAR_ARG_KEY,
        SEASON_ARG_KEY,
        GENRES_ARG_KEY,
        PAGE_ARG_KEY
    ]

    for param_key in param_keys:
        if param_key in plugin.args:
            current_params[param_key] = plugin.args[param_key][0]

    return current_params

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

    int_fields = ["sort", "year", "page", "limit"]
    mapped_ints = {}
    for x in int_fields:
        mapped_ints[x] = int(params.get(x))

    params.update(mapped_ints)

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
            plugin.url_for(
                episode_list,
                id=anime["animeID"],
                listId=anime["animeListID"],
                episode_count=anime["animeEpisode"]
            ),
            li,
            True
        )

    are_pages_remaining = math.ceil(float(json_data["data"]["count"]) / float(params["limit"])) > int(params.get("page"))
    if (are_pages_remaining):
        next_page_params = params.copy()
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
