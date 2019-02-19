import requests
import math
import logging
import xbmcaddon
import xbmc
from xbmcgui import ListItem, Dialog
from xbmcplugin import addDirectoryItem, endOfDirectory, setResolvedUrl

from resources.lib.router_factory import get_router_instance
from resources.lib.constants.url import BASE_URL, LIST_PATH

ADDON = xbmcaddon.Addon()
logger = logging.getLogger(ADDON.getAddonInfo('id'))

# Genre List: https://api.animepie.to/Anime/Genres
# data: [ 0: {id,name}]

years = [
    "ALL", # Nothing passed for year param
    "2018",
    "2017",
    "2016",
    "2015",
    "2014",
    "2013",
    "2012",
    "2011",
    "2010",
    "2009",
    "2008",
    "2007",
    "2006",
    "2005"
]

seasons = [
    "Winter",
    "Spring",
    "Summer",
    "Fall"
]

count = 0

# This might not work. Sounds like we'll need to generate a url and pass the newly selected values in
default_filter_values = {
    "year": "2018",
    "season": "Fall"
}

# filter_list_items = {
#     "year": ListItem("Year: " + default_filter_values.get("year")),
#     "season": ListItem("Seasons: " + default_filter_values.get("season"))
# }

# filter_menu_items = [
#     {
#         "filter_func": year_select,
#         "label": "Year: %s"
#     }
# ]

YEAR_ARG_KEY = "year"

def generate_routes(plugin):
    plugin.add_route(filter_screen, "/filter")
    plugin.add_route(anime_list, "/anime-list")
    plugin.add_route(genre_select, "/genre-select")
    plugin.add_route(year_select, "/anime-list/year-select")

    return plugin

def _get_current_params(plugin):
    current_params = {}

    if YEAR_ARG_KEY in plugin.args:
        current_params[YEAR_ARG_KEY] = plugin.args[YEAR_ARG_KEY][0]

    return current_params

def genre_select():
# Genre List: https://api.animepie.to/Anime/Genres
# data: [ 0: {id,name}]
    logger.debug("Genre Select")
    plugin = get_router_instance()
    # filter_list_items["year"].setLabel("2")
    # args = { "year": "2000" }
    args = {}

    xbmc.executebuiltin("RunPlugin(" + plugin.url_for(filter_screen, **args) + ")")
    # plugin.args = { "year": ["2000"] }
    # plugin.redirect("/filter")
    # plugin.redirect(plugin.url_for(filter_screen, year="2000"))

def year_select():
    logger.debug("Year Select")
    plugin = get_router_instance()
    args = _get_current_params(plugin)

    res = Dialog().select("Choose a year", years)

    if res >= 0:
        args[YEAR_ARG_KEY] = years[res]

    display_filter_menu_items(plugin, args)
    endOfDirectory(plugin.handle)

def _display_filter_menu_items(plugin, filter_values):
    generate_text = lambda label, filter_map, key: label % (filter_map[key] if key in filter_map else '')

    filter_menu_items = [
        {
            "filter_func": year_select,
            "label": "Year: %s"
        }
    ]

    for menu_item in filter_menu_items:
        addDirectoryItem(
            plugin.handle,
            plugin.url_for(menu_item.get("filter_func")),
            ListItem(generate_text(menu_item.get("label"), filter_values, YEAR_ARG_KEY)),
            True
        )

    addDirectoryItem(
        plugin.handle,
        None,
        ListItem("Search"),
        True
    )

def filter_screen():
    logger.debug("Inside filter screen")
    plugin = get_router_instance()

    display_filter_menu_items(plugin, _get_current_params(plugin))

    endOfDirectory(plugin.handle)


def anime_list():
    plugin = get_router_instance()
    filter_screen(plugin)
    page = plugin.args["page"][0] if "page" in plugin.args else None
    # page = selected_page if selected_page else "1" 

    # logger.debug("Page: " + page)

    # params = {
    #     "page": page,
    #     "limit": "15",
    #     "year": "2018",
    #     "season": "Summer",
    #     "genres": "",
    #     "sort": "1",
    #     "sort2": "",
    #     "website": ""
    # }

    # res = requests.get(BASE_URL + LIST_PATH, params=params)
    # json_data = res.json()
    # for anime in json_data["data"]["list"]:
    #     image = anime['backgroundSrc'] if anime['backgroundSrc'] else None
    #     info = anime['animeSynopsis'] if anime['animeSynopsis'] else ''

    #     li = ListItem(anime["animeName"])
    #     li.setArt({'icon': image })
    #     li.setInfo(type='video', infoLabels={'plot': info})

    #     addDirectoryItem(
    #         plugin.handle,
    #         plugin.url_for(
    #             episode_list_func,
    #             id=anime["animeID"],
    #             listId=anime["animeListID"],
    #             episode_count=anime["animeEpisode"]
    #         ), li,
    #         True
    #     )

    # are_pages_remaining = math.ceil(float(json_data["data"]["count"]) / float(params["limit"])) > int(page)
    # if (are_pages_remaining):
    #     addDirectoryItem(
    #         plugin.handle, 
    #         plugin.url_for(
    #             original_caller, page=int(page) + 1
    #         ),
    #         ListItem('Next Page'),
    #         True
    #     )

    # endOfDirectory(plugin.handle)
