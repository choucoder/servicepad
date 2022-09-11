from typing import List, Tuple
from flask_restful import Api, Resource


class CustomApi(Api):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix = '/api'

    def add_resources(self, routes: List[Tuple[str, Resource]]) -> None:
        for url, resource in routes:
            self.add_resource(resource, url)