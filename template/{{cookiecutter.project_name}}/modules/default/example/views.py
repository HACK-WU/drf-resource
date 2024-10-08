# -*- coding: utf-8 -*-

from drf_resource import resource
from drf_resource.viewsets import ResourceRoute, ResourceViewSet


class ExampleViewSet(ResourceViewSet):
    resource_routes = [
        ResourceRoute("GET", resource.example.user_info),
    ]
