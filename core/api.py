from typing import List, Tuple
from flask_restful import Api, Resource


class CustomApi(Api):
    """Class extended from flask_restful.Api"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix = '/api'

    def add_resources(self, routes: List[Tuple[str, Resource]]) -> None:
        """Add a list of routes to the API endpoints. This method
        call to add_resource from flask_restful.Api.add_resource for
        add every route -> Tuple[endpoint, Resource]

        Parameters
        ---
            routes: A list of routes
        """
        for url, resource in routes:
            self.add_resource(resource, url)