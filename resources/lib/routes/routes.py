from resources.lib.routes.index import generate_routes as generate_index_routes
from resources.lib.routes.animelist import generate_routes as generate_list_routes

def generate_all_routes(plugin):
  route_generator = [
      generate_index_routes,
      generate_list_routes
  ]

  for generator in route_generator:
      generator(plugin)

  return plugin
