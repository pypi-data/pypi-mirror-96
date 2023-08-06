# -*- coding: utf-8 -*-
"""
    pip_services3_rpc.services.HttpEndpoint
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Http endpoint implementation

    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
import json
import time
from threading import Thread

import bottle
from beaker.middleware import SessionMiddleware
from bottle import request, response
from pip_services3_commons.config import IConfigurable, ConfigParams
from pip_services3_commons.errors import ConnectionException, ConfigException
from pip_services3_commons.refer import IReferenceable
from pip_services3_commons.run import IOpenable
from pip_services3_commons.validate import Schema
from pip_services3_components.count import CompositeCounters
from pip_services3_components.log import CompositeLogger

from .HttpResponseSender import HttpResponseSender
from .SSLCherryPyServer import SSLCherryPyServer
from ..connect.HttpConnectionResolver import HttpConnectionResolver


class HttpEndpoint(IOpenable, IConfigurable, IReferenceable):
    """
    Used for creating HTTP endpoints. An endpoint is a URL, at which a given service can be accessed by a client.

    ### Configuration parameters ###
        Parameters to pass to the :func:`configure` method for component configuration:
            - connection(s) - the connection resolver's connections;
            - "connection.discovery_key" - the key to use for connection resolving in a discovery service;
            - "connection.protocol" - the connection's protocol;
            - "connection.host" - the target host;
            - "connection.port" - the target port;
            - "connection.uri" - the target URI.

    ### References ###
        A logger, counters, and a connection resolver can be referenced by passing the following references to the object's :func:`set_references` method:
            - `*:logger:*:*:1.0`           (optional) :class:`ILogger <pip_services3_components.log.ILogger.ILogger>` components to pass log messages
            - `*:counters:*:*:1.0`         (optional) :class:`ICounters <pip_services3_components.count.ICounters.ICounters>` components to pass collected measurements
            - `*:discovery:*:*:1.0`        (optional) :class:`IDiscovery <pip_services3_components.connect.IDiscovery.IDiscovery>` services to resolve connection

    Example:

    .. code-block:: python

        def my_method(_config, _references):
            endpoint = HttpEndpoint()
            if (_config)
                endpoint.configure(_config)
            if (_references)
                endpoint.setReferences(_references)
            # ...

            endpoint.open(correlationId)
            # ...
    """
    _default_config = ConfigParams.from_tuples("connection.protocol", "http",
                                               "connection.host", "0.0.0.0",
                                               "connection.port", 3000,
                                               "credential.ssl_key_file", None,
                                               "credential.ssl_crt_file", None,
                                               "credential.ssl_ca_file", None,
                                               "options.maintenance_enabled", False,
                                               "options.request_max_size", 1024 * 1024,
                                               "options.file_max_size", 200 * 1024 * 1024,
                                               "connection.connect_timeout", 60000,
                                               "connection.debug", True)

    _debug = False

    def __init__(self):
        """
        Creates HttpEndpoint
        """
        self._service = None
        self._server = None
        self._maintenance_enabled = False
        self._file_max_size = 200 * 1024 * 1024
        self._protocol_upgrade_enabled = False
        self._uri = None

        self._connection_resolver = HttpConnectionResolver()
        self._logger = CompositeLogger()
        self._counters = CompositeCounters()
        self._registrations = []

    def configure(self, config):
        """
        Configures this HttpEndpoint using the given configuration parameters.
        - connection(s) - the connection resolver's connections;
            - "connection.discovery_key" - the key to use for connection resolving in a discovery service;
            - "connection.protocol" - the connection's protocol;
            - "connection.host" - the target host;
            - "connection.port" - the target port;
            - "connection.uri" - the target URI.

        :param config: configuration parameters, containing a "connection(s)" section.
        """
        config = config.set_defaults(self._default_config)
        self._connection_resolver.configure(config)
        self._file_max_size = config.get_as_boolean_with_default('options.file_max_size', self._file_max_size)
        self._maintenance_enabled = config.get_as_long_with_default('options.maintenance_enabled',
                                                                    self._maintenance_enabled)
        self._protocol_upgrade_enabled = config.get_as_boolean_with_default('options.protocol_upgrade_enabled',
                                                                            self._protocol_upgrade_enabled)
        self._debug = config.get_as_boolean_with_default('connection.debug', self._debug)

    def set_references(self, references):
        """
        Sets references to this endpoint's logger, counters, and connection resolver.

        - *:logger:*:*:1.0           (optional) :class:`ILogger <pip_services3_components.log.ILogger.ILogger>` components to pass log messages
        - *:counters:*:*:1.0         (optional) :class:`ICounters <pip_services3_components.count.ICounters.ICounters>` components to pass collected measurements
        - *:discovery:*:*:1.0        (optional) :class:`IDiscovery <pip_services3_components.connect.IDiscovery.IDiscovery>` services to resolve connection

        :param references: an IReferences object, containing references to a logger, counters, and a connection resolver.
        """
        self._logger.set_references(references)
        self._counters.set_references(references)
        self._connection_resolver.set_references(references)

    def is_opened(self):
        """
        Checks if the component is opened.

        :return: whether or not this endpoint is open with an actively listening REST server.
        """
        return not (self._server is None)

    def open(self, correlation_id):
        """
        Opens a connection using the parameters resolved by the referenced connection resolver and creates a REST server (service) using the set options and parameters.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        if self.is_opened():
            return

        connection = self._connection_resolver.resolve(correlation_id)
        if connection is None:
            raise ConfigException(correlation_id, "NO_CONNECTION", "Connection for REST client is not defined")
        self._uri = connection.get_uri()

        # verify https with bottle

        certfile = None
        keyfile = None

        if connection.get_protocol('http') == 'https':
            certfile = connection.get_as_nullable_string('ssl_crt_file')
            keyfile = connection.get_as_nullable_string('ssl_key_file')

        # Create instance of bottle application
        self._service = SessionMiddleware(bottle.Bottle(catchall=True, autojson=True)).app

        self._service.config['catchall'] = True
        self._service.config['autojson'] = True

        # Enable CORS requests
        self._service.add_hook('after_request', self._enable_cors)
        self._service.route('/', 'OPTIONS', self._options_handler)
        self._service.route('/<path:path>', 'OPTIONS', self._options_handler)

        self._service.add_hook('after_request', self._do_maintance)
        self._service.add_hook('after_request', self._no_cache)
        self._service.add_hook('before_request', self._add_compatibility)

        # Register routes
        # self.perform_registrations()

        def start_server():
            self._service.run(server=self._server, debug=self._debug)

        # self.perform_registrations()

        host = connection.get_host()
        port = connection.get_port()
        # Starting service
        try:
            self._server = SSLCherryPyServer(host=host, port=port, certfile=certfile, keyfile=keyfile)

            # Start server in thread
            Thread(target=start_server).start()
            # Time for start server
            time.sleep(0.01)

            # Give 2 sec for initialization
            self._connection_resolver.register(correlation_id)
            self._logger.debug(correlation_id, f"Opened REST service at {self._uri}", )
            self.perform_registrations()
        except Exception as ex:
            self._server = None

            raise ConnectionException(correlation_id, 'CANNOT_CONNECT', 'Opening REST service failed') \
                .wrap(ex).with_details('url', self._uri)

    def close(self, correlation_id):
        """
        Closes this endpoint and the REST server (service) that was opened earlier.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        try:
            if not (self._server is None):
                self._server.shutdown()
                self._service.close()
                self._logger.debug(
                    correlation_id, f"Closed REST service at {self._uri}")

            self._server = None
            self._service = None
            self._uri = None
        except Exception as ex:
            self._logger.warn(correlation_id, "Failed while closing REST service: " + str(ex))

    def register(self, registration):
        """
        Registers a registerable object for dynamic endpoint discovery.

        :param registration: the registration to add.
        """
        self._registrations.append(registration)

    def unregister(self, registration):
        """
        Unregisters a registerable object, so that it is no longer used in dynamic endpoint discovery.

        :param registration: the registration to remove.
        """
        self._registrations.remove(registration)

    def perform_registrations(self):
        for registration in self._registrations:
            registration.register()

    def fix_route(self, route) -> str:
        if route is not None and len(route) > 0:
            if route[0] != '/':
                route = f'/{route}'
            return route

        return ''

    def register_route(self, method, route, schema, handler):
        """
        Registers an action in this objects REST server (service) by the given method and route.

        :param method: the HTTP method of the route.

        :param route: the route to register in this object's REST server (service).

        :param schema: the schema to use for parameter validation.

        :param handler: the action to perform at the given route.
        """
        method = method.upper()
        # if method == 'DELETE':
        #     method = 'DEL'

        route = self.fix_route(route)

        def wrapper(*args, **kwargs):
            try:
                if isinstance(schema, Schema):
                    params = self.get_data()
                    correlation_id = None if not params else params.get('correlation_id')
                    schema.validate_and_throw_exception(correlation_id, params, False)
                return handler(*args, **kwargs)
            except Exception as ex:
                # hack the redirect response in bottle
                if isinstance(ex, bottle.HTTPResponse):
                    handler(*args, **kwargs)
                return HttpResponseSender.send_error(ex)

        self._service.route(route, method, wrapper)

    def get_data(self):
        result = {}
        if request.json or request.query:
            for k, v in request.query.dict.items():
                result[k] = ''.join(v)
            if request.json != 'null':
                result.update(request.json if not isinstance(request.json, str) else json.loads(
                    request.json))
            return result
        else:
            return None

    def _enable_cors(self):
        response.headers['Access-Control-Max-Age'] = '5'
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
        response.headers[
            'Access-Control-Allow-Headers'] = 'Authorization, Origin, Accept, Content-Type, X-Requested-With'

    def _do_maintance(self):
        """
        :return: maintenance error code
        """
        # Make this more sophisticated
        if self._maintenance_enabled:
            response.headers['Retry-After'] = 3600
            response.status = 503

    def _no_cache(self):
        """
        Prevents IE from caching REST requests
        """
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = 0

    def _add_compatibility(self):

        def inner(name):
            if request.query:
                param = request.query[name]
                if param:
                    return param
            if request.body:
                param = request.json[name]
                if param:
                    return param
            if request.params:
                param = request.params[name]
                if param:
                    return param

            return None

        request['param'] = inner
        request['route'] = {'params': request.params}

    def _options_handler(self, ath=None):
        return

    def get_param(self, param, default=None):
        return request.params.get(param, default)

    def get_correlation_id(self):
        return request.query.get('correlation_id')

    def register_route_with_auth(self, method, route, schema, authorize, action):
        """
        Registers an action with authorization in this objects REST server (service)
        by the given method and route.

        :param method: the HTTP method of the route.
        :param route: the route to register in this object's REST server (service).
        :param schema: the schema to use for parameter validation.
        :param authorize: the authorization interceptor
        :param action: the action to perform at the given route.
        """
        if authorize:
            next_action = action
            action = lambda req, res: authorize(request, response, next_action(response, response))

        self.register_route(method, route, schema, action)

    def register_interceptor(self, route, action):
        """
        Registers a middleware action for the given route.

        :param route: the route to register in this object's REST server (service).
        :param action: the middleware action to perform at the given route.
        """
        route = self.fix_route(route)

        self._service.add_hook('before_request', lambda: action(request, response) if not (
                route is not None and route != '' and str(request.url).startswith(route)) else None)
