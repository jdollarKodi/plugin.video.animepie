import requests
import math
import logging
import xbmcaddon
from xbmcgui import ListItem
from xbmcplugin import addDirectoryItem, endOfDirectory

from resources.lib.constants.url import BASE_URL, LIST_PATH

ADDON = xbmcaddon.Addon()
logger = logging.getLogger(ADDON.getAddonInfo('id'))

def anime_list(plugin, selected_page, episode_list_func, original_caller):
    page = selected_page if selected_page else "1" 

    logger.debug("Page: " + page)

    params = {
        "page": page,
        "limit": "15",
        "year": "2018",
        "season": "Summer",
        "genres": "",
        "sort": "1",
        "sort2": "",
        "website": ""
    }

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
                episode_list_func,
                id=anime["animeID"],
                listId=anime["animeListID"],
                episode_count=anime["animeEpisode"]
            ), li,
            True
        )

    are_pages_remaining = math.ceil(float(json_data["data"]["count"]) / float(params["limit"])) > int(page)
    if (are_pages_remaining):
        addDirectoryItem(
            plugin.handle, 
            plugin.url_for(
                original_caller, page=int(page) + 1
            ),
            ListItem('Next Page'),
            True
        )

    endOfDirectory(plugin.handle)
