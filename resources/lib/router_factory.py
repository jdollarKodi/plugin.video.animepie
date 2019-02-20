import sys
import routing

this = sys.modules[__name__]
this.instance = None

def get_router_instance():
    if not this.instance:
        this.instance = routing.Plugin()

    return this.instance
