# -*- coding: utf-8 -*-
# Copyright © 2020 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.extern.six import iteritems

import contrast
from contrast.agent.assess.policy.source_policy import cs__apply_source
from contrast.agent.policy.trigger_node import TriggerNode
from contrast.agent.middlewares.base_middleware import BaseMiddleware
from contrast.agent.middlewares.environ_tracker import (
    build_source_node,
    track_environ_sources,
)
from contrast.agent.middlewares.route_coverage.pyramid_routes import (
    create_pyramid_routes,
    get_view_func,
    build_pyramid_route,
)
from contrast.agent.request_context import RequestContext
from contrast.utils.decorators import cached_property, fail_safely
from contrast.utils.exceptions.contrast_service_exception import (
    ContrastServiceException,
)

from contrast.extern import structlog as logging
from pyramid.interfaces import IRoutesMapper

logger = logging.getLogger("contrast")


REQUEST_SOURCES = {
    "body": "BODY",
    "host_url": "PARAMETER",
    "path": "PARAMETER",
    "path_info": "PARAMETER",
    "query_string": "PARAMETER",
    "remote_addr": "PARAMETER",
    "text": "BODY",
    "url": "PARAMETER",
}

WEBOB = "webob"


class PyramidMiddleware(BaseMiddleware):
    def __init__(self, handler, registry):
        self.registry = registry
        self.app_name = self.get_app_name()

        super(PyramidMiddleware, self).__init__()

        self.handler = handler

    def get_app_name(self):
        try:
            return self.registry.package_name
        except Exception:
            return "pyramid_app"

    def __call__(self, request):
        if self.is_agent_enabled() and request:
            environ = request.environ

            context = RequestContext(environ)

            if self.settings.is_assess_enabled():
                self.track_sources(context, request, environ)

            with contrast.CS__CONTEXT_TRACKER.lifespan(context):
                return self.call_with_agent(request, context, environ)

        return self.call_without_agent(request)

    def call_without_agent(self, request):
        """
        Normal without middleware call
        """
        super(PyramidMiddleware, self).call_without_agent()
        return self.handler(request)

    def call_with_agent(self, request, context, environ):
        self.log_start_request_analysis(environ.get("PATH_INFO"))

        context.timer.set_start("total")

        try:
            self.prefilter(context)

            logger.debug("Start app code and get response")
            response = self.handler(request)
            logger.debug("Finished app code and get response")

            # Pyramid's response class is based on Webob's, which already
            # implements BaseResponseWrapper's requirements
            context.extract_response_to_context(response)

            self.postfilter(context)

            self.check_for_blocked(context)

            context.timer.set_end("total")

            return response
        except ContrastServiceException as e:
            logger.warning(e)
            return self.call_without_agent(request)
        except Exception as e:
            return self.handle_exception(e)
        finally:
            self.handle_ensure(context, request)
            self.log_end_request_analysis(context.request.path)
            if self.settings.is_assess_enabled():
                contrast.STRING_TRACKER.ageoff()

    @fail_safely("Unable to get route coverage", return_value={})
    def get_route_coverage(self):
        return create_pyramid_routes(self.registry)

    @cached_property
    def trigger_node(self):
        method_name = self.handler.__name__

        module, class_name, args, instance_method = self._process_trigger_handler(
            self.handler
        )

        return (
            TriggerNode(module, class_name, instance_method, method_name, "RETURN"),
            args,
        )

    @fail_safely("Unable to find new routes")
    def get_view_func(self, request):
        path = request.environ.get("PATH_INFO", "")
        if not path:
            logger.debug("No path info for pyramid request")
            return None

        mapper = self.registry.queryUtility(IRoutesMapper)
        routes = mapper.get_routes()

        # Ideally we would like to call get_route but
        # there is no direct relationship between the wsgi
        # request path and the name of the route so we must
        # iterate over all the routes to find it by the path
        # pyramid_route = mapper.get_route(name)

        matching_routes = [x for x in routes if x.path == path]
        if not matching_routes:
            return None

        return get_view_func(self.registry, matching_routes[0])

    @fail_safely("Unable to build route", return_value="")
    def build_route(self, view_func, url):
        route_name = url.replace("/", "")
        return build_pyramid_route(route_name, view_func)

    def generate_security_exception_response(self):
        from pyramid.httpexceptions import HTTPForbidden

        return HTTPForbidden(explanation=self.OVERRIDE_MESSAGE)

    def track_sources(self, context, request, environ):
        """
        This method will track necessary information in the environ and all the properties in a Webob request

        If information is changed or updated by the application after application code executes we do not care
        because the information is then deemed trusted

        :param context: current request context
        :param request: Pyramid Webob request
        :param environ: environ dict provided by framework
        :return: None
        """
        track_environ_sources(WEBOB, context, environ)

        for key, source_type in iteritems(REQUEST_SOURCES):
            source = getattr(request, key)

            node = build_source_node(WEBOB, key, source_type)

            cs__apply_source(context, node, source, request, source, (), {})
