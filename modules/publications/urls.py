from .resources import (
    PublicationResource, SinglePublicationResource,
    UserPublicationsResource,
)


routes = [
    ('/publications', PublicationResource),
    ('/publications/<int:id>', SinglePublicationResource),
    ('/users/<int:id>/publications', UserPublicationsResource),
]