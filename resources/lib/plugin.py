# -*- coding: utf-8 -*-

import xbmc
import routing
import logging
import xbmcaddon
import requests
from bs4 import BeautifulSoup
from resources.lib import kodiutils, kodilogging
from resources.lib.animepie_exception import AnimePieException
from resources.lib.embed_processors import mp4upload, streamango
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
def index():
    addDirectoryItem(plugin.handle, plugin.url_for(anime_list), ListItem("Anime List"), True)
    addDirectoryItem(plugin.handle, plugin.url_for(anime_search), ListItem('Search'), True)
    endOfDirectory(plugin.handle)

@plugin.route('/anime-list')
def anime_list():
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
            plugin.url_for(
                episode_list,
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

@plugin.route('search')
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
        "ASTV.MP4UPLOAD": mp4upload,
        "9A.Streamango": streamango
    }

    decrypted_source = None
    processor = embedded_processors.get(website_name, None)

    try:
        if processor:
            res = requests.get(source_url)
            soup = BeautifulSoup(res.text, 'html.parser')
            if processor:
                (err, decrypted_source) = processor.retrieve_source_url(soup)

                if err:
                    raise err

            if (decrypted_source):
                play_item = ListItem(path=decrypted_source)
                xbmc.Player().play(decrypted_source, play_item)
        
        if not processor and not decrypted_source:
            raise AnimePieException(ADDON.getLocalizedString(32001))
    except AnimePieException as e:
        logger.error(e.args)
        xbmc.executebuiltin("Notification(Error," + e.args[0] + ")")
    except Exception as e:
        logger.error(e.args)
        xbmc.executebuiltin("Notification(Error," + str(e.args) + ")")

def run():
    plugin.run()
