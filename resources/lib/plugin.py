# -*- coding: utf-8 -*-

import xbmc
import routing
import logging
import xbmcaddon
import requests
from bs4 import BeautifulSoup
from resources.lib import kodiutils
from resources.lib import kodilogging
from resources.lib.embed_processors import streamango
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
    logger.debug("Anime list")

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

    res = requests.get(BASE_URL + LIST_PATH, params=params)
    json_data = res.json()
    for anime in json_data["data"]["list"]:
        addDirectoryItem(plugin.handle, plugin.url_for(
            episode_list, id=anime["animeID"], listId=anime["animeListID"], episode_count=anime["animeEpisode"]), ListItem(anime["animeName"]), True)
        logger.debug(anime["animeName"])
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
        addDirectoryItem(plugin.handle, plugin.url_for(
            video_sources, id=anime_id, listId=anime_list_id, episode=episode), ListItem("Episode " + episode), True)

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
        for src in source["srclist"]:
            addDirectoryItem(plugin.handle, plugin.url_for(play_source, source_url=src["src"], website_name=src["website"]), ListItem(src["website"]), True)

    endOfDirectory(plugin.handle)

@plugin.route('/video-source/play')
def play_source():
    website_name = plugin.args["website_name"][0]
    source_url = plugin.args["source_url"][0]

    logger.debug("Website: " + website_name)
    logger.debug("Source URL: " + source_url)

    res = requests.get(source_url)
    soup = BeautifulSoup(res.text, 'html.parser')

    decrypted_source = None
    if (website_name == "9A.Streamango"):
        decrypted_source = streamango.retrieve_source_url(soup)

    if (decrypted_source):
        play_item = ListItem(path=decrypted_source)
        xbmc.Player().play(decrypted_source, play_item)
    else:
        logger.error('invalid source')

@plugin.route('/category/<category_id>')
def show_category(category_id):
    addDirectoryItem(
        plugin.handle, "", ListItem("Hello category %s!" % category_id))
    endOfDirectory(plugin.handle)

def run():
    plugin.run()
