import logging
import xbmcaddon
from xbmcgui import ListItem
from xbmcplugin import addDirectoryItem, endOfDirectory
from resources.lib.router_factory import get_router_instance
from resources.lib.routes.videosources import video_sources

ADDON = xbmcaddon.Addon()
logger = logging.getLogger(ADDON.getAddonInfo('id'))

def generate_routes(plugin):
    plugin.add_route(episode_list, "/episode-list")

    return plugin

def episode_list():
    plugin = get_router_instance()
    anime_id = plugin.args["id"][0]
    anime_list_id = plugin.args["listId"][0]
    episode_count = plugin.args["episode_count"][0]

    episode_str = ADDON.getLocalizedString(32004)

    for i in range(int(episode_count)):
        episode = str(i + 1)
        addDirectoryItem(
            plugin.handle, 
            plugin.url_for(
                video_sources,
                id=anime_id,
                listId=anime_list_id,
                episode=episode
            ),
            ListItem(episode_str % episode), 
            True
        )

    endOfDirectory(plugin.handle)
