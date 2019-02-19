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
from resources.lib.routes.routes import generate_all_routes
from resources.lib.router_factory import get_router_instance
from itertools import repeat
from xbmcgui import ListItem
from xbmcplugin import addDirectoryItem, endOfDirectory, setResolvedUrl

ADDON = xbmcaddon.Addon()
logger = logging.getLogger(ADDON.getAddonInfo('id'))
kodilogging.config()
plugin = get_router_instance()

BASE_URL="https://api.animepie.to"
LIST_PATH="/Anime/AnimeMain/List"
HOME_DETAIL_PATH="/Anime/AnimeMain/HomeDetail"

@plugin.route('/search')
def anime_search():
    logger.debug('Search')
    endOfDirectory(plugin.handle)

def run():
    generate_all_routes(plugin)
    plugin.run()
