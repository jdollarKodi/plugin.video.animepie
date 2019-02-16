# -*- coding: utf-8 -*-

import xbmcaddon
import logging
import js2py
from resources.lib.animepie_exception import AnimePieException

ADDON = xbmcaddon.Addon()
logger = logging.getLogger(ADDON.getAddonInfo('id'))

def retrieve_source_url(soup):
  body = soup.find('body')

  if not body:
    return (AnimePieException("File was deleted"), None)
  else:
    return (AnimePieException("Not yet implemented"), None)
