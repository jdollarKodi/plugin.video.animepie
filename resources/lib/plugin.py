# -*- coding: utf-8 -*-

import logging
import xbmcaddon
from resources.lib import kodiutils, kodilogging
from resources.lib.routes.routes import generate_all_routes

ADDON = xbmcaddon.Addon()
logger = logging.getLogger(ADDON.getAddonInfo('id'))
kodilogging.config()

def run():
    plugin = get_router_instance()
    generate_all_routes(plugin)
    plugin.run()
