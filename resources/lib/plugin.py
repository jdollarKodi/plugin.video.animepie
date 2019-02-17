# -*- coding: utf-8 -*-

import xbmc
import routing
import logging
import xbmcaddon
import requests
import resolveurl
from bs4 import BeautifulSoup
from resources.lib import kodiutils, kodilogging
from resources.lib.animepie_exception import AnimePieException
from resources.lib.embed_processors import mp4upload, streamango
from resources.lib.routes.index import index
from resources.lib.routes.animelist import anime_list
from itertools import repeat
from xbmcgui import ListItem
from xbmcplugin import addDirectoryItem, endOfDirectory, setResolvedUrl

ADDON = xbmcaddon.Addon()
logger = logging.getLogger(ADDON.getAddonInfo('id'))
kodilogging.config()
plugin = routing.Plugin()

BASE_URL="https://api.animepie.to"
LIST_PATH="/Anime/AnimeMain/List"
HOME_DETAIL_PATH="/Anime/AnimeMain/HomeDetail"

@plugin.route('/')
def root():
    index(plugin)

@plugin.route('/anime-list')
def full_list():
    anime_list(plugin, episode_list, full_list)

@plugin.route('/search')
def anime_search():
    logger.debug('Search')
    endOfDirectory(plugin.handle)

@plugin.route('/episode-list')
def episode_list():
    anime_id = plugin.args["id"][0]
    anime_list_id = plugin.args["listId"][0]
    episode_count = plugin.args["episode_count"][0]

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
            ListItem("Episode " + episode), 
            True
        )

    endOfDirectory(plugin.handle)

@plugin.route('/video-sources')
def video_sources():
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

@plugin.route('/video-source/play')
def play_source():
    website_name = plugin.args["website_name"][0]
    source_url = plugin.args["source_url"][0]

    logger.debug("Website: " + website_name)
    logger.debug("Source URL: " + source_url)

    embedded_processors = {
        "MP4UPLOAD": mp4upload,
        "Streamango": streamango,
    }

    decrypted_source = None
    processor = embedded_processors.get(website_name.split(".")[1], None)

    try:
        if processor:
            res = requests.get(source_url)
            soup = BeautifulSoup(res.text, 'html.parser')
            if processor:
                (err, decrypted_source) = processor.retrieve_source_url(soup)

                if err:
                    raise err
        else:
            For sources without custom logic use the urlresolver package
            decrypted_source = resolveurl.resolve(source_url)
            logger.debug(decrypted_source)
        
        if not processor and not decrypted_source:
            raise AnimePieException(ADDON.getLocalizedString(32001))
        elif decrypted_source:
            play_item = ListItem(path=decrypted_source)
            xbmc.Player().play(decrypted_source, play_item)

    except AnimePieException as e:
        logger.error(e.args)
        xbmc.executebuiltin("Notification(Error," + e.args[0] + ")")

def run():
    plugin.run()
