import xbmc
import requests
import logging
import xbmcaddon
import resolveurl
from bs4 import BeautifulSoup
from xbmcgui import ListItem
from xbmcplugin import addDirectoryItem, endOfDirectory
from resources.lib.router_factory import get_router_instance
from resources.lib.embed_processors import mp4upload, streamango
from resources.lib.animepie_exception import AnimePieException

ADDON = xbmcaddon.Addon()
logger = logging.getLogger(ADDON.getAddonInfo('id'))

def generate_routes(plugin):
    plugin.add_route(play_source, "/video-source/play")

    return plugin


def play_source():
    plugin = get_router_instance()
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
            # For sources without custom logic use the urlresolver package
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
