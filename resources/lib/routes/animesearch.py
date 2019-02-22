import requests
import logging
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
    search_value = plugin.args["search"][0] if "search" in plugin.args else ""
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

    endOfDirectory(plugin.handle)
