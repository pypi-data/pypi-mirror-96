# -*- coding: utf-8 -*-
"""
    pip_services3_rpc.services.StatusRestService
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Status rest service implementation

    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
import datetime

from pip_services3_commons.convert import StringConverter
from pip_services3_commons.refer import Descriptor
from pip_services3_commons.run import Parameters

from .RestService import RestService


class StatusRestService(RestService):
    """
    Service that returns microservice status information via HTTP/REST protocol. The service responds on /status route (can be changed) with a JSON object:
    
    .. code-block:: json
    
        {
            - "id":            unique container id (usually hostname)
            - "name":          container name (from ContextInfo)
            - "description":   container description (from ContextInfo)
            - "start_time":    time when container was started
            - "current_time":  current time in UTC
            - "uptime":        duration since container start time in milliseconds
            - "properties":    additional container properties (from ContextInfo)
            - "components":    descriptors of components registered in the container
        }

    ### Configuration parameters ###
        - base_route:              base route for remote URI
        - dependencies:
            - endpoint:              override for HTTP Endpoint dependency
            - controller:            override for Controller dependency
        - connection(s):
            - discovery_key:         (optional) a key to retrieve the connection from IDiscovery
            - protocol:              connection protocol: http or https
            - host:                  host name or IP address
            - port:                  port number
            - uri:                   resource URI or connection string with all parameters in it

    ### References ###
        - `*:logger:*:*:1.0`           (optional) :class:`ILogger <pip_services3_components.log.ILogger.ILogger>` components to pass log messages
        - `*:counters:*:*:1.0`         (optional) :class:`ICounters <pip_services3_components.count.ICounters.ICounters>` components to pass collected measurements
        - `*:discovery:*:*:1.0`        (optional) :class:`IDiscovery <pip_services3_components.connect.IDiscovery.IDiscovery>` services to resolve connection
        - `*:endpoint:http:*:1.0`      (optional) :class:`HttpEndpoint <pip_services3_rpc.services.HttpEndpoint>` reference

    Example:

    .. code-block:: python

          service = StatusService()
          service.configure(ConfigParams.from_tuples("connection.protocol", "http",
                                                     "connection.host", "localhost",
                                                     "connection.port", 8080))
          service.open("123")
          # ...
    """
    _start_time = datetime.datetime.now()
    _references2 = None
    _context_info = None
    _route = "status"

    def __init__(self):
        """
        Creates a new instance of this service.
        """
        super(StatusRestService, self).__init__()
        self._dependency_resolver.put("context-info", Descriptor("pip-services", "context-info", "default", "*", "1.0"))

    def configure(self, config):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        super(StatusRestService, self).configure(config)

        self._route = config.get_as_string_with_default("route", self._route)

    def set_references(self, references):
        """
        Sets references to dependent components.

        :param references: references to locate the component dependencies.
        """
        self._references2 = references
        super(StatusRestService, self).set_references(references)
        self._context_info = self._dependency_resolver.get_one_optional("context-info")

    def register(self):
        """
        Registers all service routes in HTTP endpoint.
        """
        # self.register_route("GET", self._route, lambda req, res: self.status(req, res))
        self.register_route("GET", self._route, None, self.status)

    # def status(self, req=None, res=None):
    def status(self):
        _id = self._context_info.context_id if not (self._context_info is None) else ""
        name = self._context_info.name if not (self._context_info is None) else "unknown"
        description = self._context_info.description if not (self._context_info is None) else ""
        uptime = (datetime.datetime.now() - self._start_time).total_seconds() * 1000
        properties = self._context_info.properties if not (self._context_info is None) else ""

        components = []
        if not (self._references2 is None):
            for locator in self._references2.get_all_locators():
                components.append(locator.__str__())

        status = Parameters.from_tuples("id", _id,
                                        "name", name,
                                        "description", description,
                                        "start_time", StringConverter.to_string(self._start_time),
                                        "current_time", StringConverter.to_string(datetime.datetime.now()),
                                        "uptime", uptime,
                                        "properties", properties,
                                        "components", components
                                        )
        return self.send_result(status)
 