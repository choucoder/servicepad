from .resources import (
    LoginResource, SingleUserResource, UserResource,
)


routes = [
    ('/users', UserResource),
    ('/users/<int:id>', SingleUserResource),
    ('/users/login', LoginResource),
]