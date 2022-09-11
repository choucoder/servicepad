from typing import List, Tuple
from importlib import import_module

from flask_restful import Resource


def get_routes(modulesDir='modules', version='v1') -> List[Tuple[str, Resource]]:
    routes = []
    modules = import_module(modulesDir).__all__

    for module in modules:
        try:
            module = import_module(f'{modulesDir}.{module}.urls')
            for url, resource in module.routes:
                url = f"/{version}{url}"
                routes.append((url, resource))
        except ModuleNotFoundError as e:
            pass
    return routes