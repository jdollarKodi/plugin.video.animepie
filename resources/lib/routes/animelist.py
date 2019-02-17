import requests
import logging
import xbmcaddon
from xbmcgui import ListItem
from xbmcplugin import addDirectoryItem, endOfDirectory

from resources.lib.constants.url import BASE_URL, LIST_PATH

ADDON = xbmcaddon.Addon()
logger = logging.getLogger(ADDON.getAddonInfo('id'))

def anime_list(plugin):
    page = plugin.args["page"][0] if "page" in plugin.args else None

    page = page if page else "1" 

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
        addDirectoryItem(
            plugin.handle,
            plugin.url_for_path(
                "/episode-list",
                id=anime["animeID"],
                listId=anime["animeListID"],
                episode_count=anime["animeEpisode"]
            ), ListItem(anime["animeName"]),
            True
        )
        logger.debug(anime["animeName"])

    addDirectoryItem(
        plugin.handle, 
        plugin.url_for(
            anime_list, page=int(page) + 1
        ),
        ListItem('Next Page'),
        True
    )

    endOfDirectory(plugin.handle)
