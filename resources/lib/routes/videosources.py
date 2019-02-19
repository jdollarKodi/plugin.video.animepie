import requests
import logging
import xbmcaddon
from xbmcgui import ListItem
from xbmcplugin import addDirectoryItem, endOfDirectory
from resources.lib.router_factory import get_router_instance
from resources.lib.constants.url import BASE_URL, HOME_DETAIL_PATH
from resources.lib.routes.playsource import play_source

ADDON = xbmcaddon.Addon()
logger = logging.getLogger(ADDON.getAddonInfo('id'))

def generate_routes(plugin):
    plugin.add_route(video_sources, "/video-sources")

    return plugin

def video_sources():
    plugin = get_router_instance()
    anime_id = plugin.args["id"][0]
    anime_list_id = plugin.args["listId"][0]
    episode_selection = plugin.args["episode"][0]

    logger.debug("Anime ID: " + anime_id)
    logger.debug("Anime List ID: " + anime_list_id)
    logger.debug("Episode: " + episode_selection)

    params = {
        "id": anime_id,
        "listid": anime_list_id,
        "episode": episode_selection
    }

    res = requests.get(BASE_URL + HOME_DETAIL_PATH, params=params)
    json_data = res.json()

    for source in json_data["data"]["animeWebSiteSrc"]:
        # Website only does the first link. We're using all defined though
        for src in source["srclist"]:
            addDirectoryItem(
                plugin.handle,
                plugin.url_for(
                    play_source,
                    source_url=src["src"],
                    website_name=src["website"]
                ),
                ListItem(src["website"]),
                True
            )

    endOfDirectory(plugin.handle)
