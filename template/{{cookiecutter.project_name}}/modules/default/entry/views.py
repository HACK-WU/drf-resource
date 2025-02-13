# -*- coding: utf-8 -*-

from drf_resource import resource
from drf_resource.viewsets import ResourceRoute, ResourceViewSet


class ViewSet(ResourceViewSet):
    resource_routes = [
        ResourceRoute("GET", resource.entry.home),
        ResourceRoute("GET", resource.entry.healthz, endpoint="healthz"),
        ResourceRoute("GET", resource.entry.ping, endpoint="ping"),
    ]
