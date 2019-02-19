import sys
import routing

this = sys.modules[__name__]
this.instance = None

def get_router_instance():
    if not this.instance:
        this.instance = routing.Plugin()

    return this.instance
# class RouterFactory:
#   instance = None

#   @staticmethod
#   def getInstance():
#       if not RouterFactory.instance:
#           RouterFactory.instance = routing.Plugin()

#       return RouterFactory.instance
