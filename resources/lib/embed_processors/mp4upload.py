# -*- coding: utf-8 -*-

import xbmcaddon
import logging
import js2py
from resources.lib.animepie_exception import AnimePieException

ADDON = xbmcaddon.Addon()
logger = logging.getLogger(ADDON.getAddonInfo('id'))

def retrieve_source_url(soup):
  player_div = soup.find('div', id="player")

  if not player_div:
    return (AnimePieException(ADDON.getLocalizedString(32000)), None)
  else:
    context = js2py.EvalJs()
    player_script = player_div.contents[0].text

    # Define some javascript so when the jwplayer is initialized we can
    # pull the src defined when the player script is run. Player script
    # uses addButton and on in various places so we define them so it doesn't
    # cause an exception and then define a jwplayer_config object that gets
    # populated with the values from when the jwplayer is initialized
    # The initialization options passed in contains file which is the src for the player
    custom_script = '''
    var jwplayer_config = null
    var jwplayer = function() {
      return {
        setup: function(opts) {
          jwplayer_config = opts;
        },
        addButton: function() {},
        on: function() {}
      };
    }
    '''

    context.execute(custom_script)
    context.execute(player_script)

    logger.debug(context.jwplayer_config["file"])
    return (None, context.jwplayer_config["file"])
