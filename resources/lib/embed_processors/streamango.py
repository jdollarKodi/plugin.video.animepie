# -*- coding: utf-8 -*-

import xbmcaddon
import logging
import js2py

ADDON = xbmcaddon.Addon()
logger = logging.getLogger(ADDON.getAddonInfo('id'))

def retrieve_source_url(soup):
    # Url generation function is in the first anonymous script block after the video container
    script = soup.find('div', class_="videocontainer").find_next_sibling('script')
    context = js2py.EvalJs()

    # Split on the first call to jquery and just run the first bit of the script tag. 
    # That handles generating the decrypt function and populating the srces variable with
    # the decrypted url
    context.execute(script.text.split('$(document)')[0])

    src_url = 'https:' + context.srces[0]['src']
    logger.debug('Decoded source url: ' + src_url)
    return src_url
