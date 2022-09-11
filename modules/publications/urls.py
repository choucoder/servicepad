from .resources import PublicationResource, SinglePublicationResource


routes = [
    ('/publications', PublicationResource),
    ('/publications/<int:id>', SinglePublicationResource),
]