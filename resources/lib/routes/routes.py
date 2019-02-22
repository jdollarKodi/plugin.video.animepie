from resources.lib.routes.index import generate_routes as generate_index_routes
from resources.lib.routes.animelist import generate_routes as generate_list_routes
from resources.lib.routes.episodelist import generate_routes as generate_episode_list_routes
from resources.lib.routes.videosources import generate_routes as generate_video_sources_routes
from resources.lib.routes.playsource import generate_routes as generate_play_source_routes
from resources.lib.routes.animesearch import generate_routes as generate_anime_search_routes
from resources.lib.routes.searchfilter import generate_routes as generate_search_filter_routes

def generate_all_routes(plugin):
  route_generator = [
      generate_index_routes,
      generate_list_routes,
      generate_episode_list_routes,
      generate_video_sources_routes,
      generate_play_source_routes,
      generate_anime_search_routes,
      generate_search_filter_routes
  ]

  for generator in route_generator:
      generator(plugin)

  return plugin
