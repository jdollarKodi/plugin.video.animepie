import requests
import logging
import math
import xbmcaddon
from xbmcgui import ListItem
from xbmcplugin import addDirectoryItem, endOfDirectory
from resources.lib.constants.url import BASE_URL, SEARCH_PATH
from resources.lib.router_factory import get_router_instance
from resources.lib.routes.episodelist import episode_list

ADDON = xbmcaddon.Addon()
logger = logging.getLogger(ADDON.getAddonInfo('id'))

def generate_routes(plugin):
    plugin.add_route(anime_search, "/search")

    return plugin

def anime_search():
    plugin = get_router_instance()
    search_value = plugin.args["name"][0] if "name" in plugin.args else ""
    page = plugin.args["page"][0] if "page" in plugin.args else "1"

    params = {
        "name": search_value,
        "limit": 10,
        "page": int(page)
    }

    res = requests.get(BASE_URL + SEARCH_PATH, params=params)
    json_data = res.json()

    for anime in json_data['data']['list']:
        li = ListItem(anime["animeName"])
        li.setArt({"icon": anime["backgroundSrc"]})
        li.setInfo(type="video", infoLabels={"plot": anime["animeSynopsis"]})

        addDirectoryItem(
            plugin.handle,
            plugin.url_for(
                episode_list,
                id=str(anime["animeID"]),
                listId=str(anime["animeListID"]),
                episode_count=str(anime["animeEpisode"])
            ),
            li,
            True
        )

    are_pages_remaining = math.ceil(float(json_data["data"]["count"]) / float(params.get("limit"))) > int(page)
    if (are_pages_remaining):
        next_page_params = { "page": page, "name": search_value }
        next_page_params.update({ "page": str(int(params.get("page")) + 1) })

        addDirectoryItem(
            plugin.handle, 
            plugin.url_for(
                anime_search, **next_page_params
            ),
            ListItem('Next Page'),
            True
        )

    endOfDirectory(plugin.handle)
