# -*- coding: utf-8 -*-
from typing import List

from pip_services3_commons.commands import ICommand
from pip_services3_commons.config import ConfigParams
from pip_services3_commons.convert import TypeCode


class CommandableSwaggerDocument:

    def __init__(self, base_route, config: ConfigParams, commands: List[ICommand]):
        self._content = ''

        self.commands: List[ICommand] = commands or []

        config = config or ConfigParams()

        self.version = '3.0.2'
        self.base_route = base_route

        self.info_title = config.get_as_string_with_default("name", "CommandableHttpService")
        self.info_description = config.get_as_string_with_default("description", "Commandable microservice")
        self.info_version = '1'
        self.info_terms_of_service = None

        self.info_contact_name = None
        self.info_contact_url = None
        self.info_contact_email = None

        self.info_license_name = None
        self.info_license_url = None

    def to_string(self):
        data = {
            'openapi': self.version,
            'info': {
                'title': self.info_title,
                'description': self.info_description,
                'version': self.info_version,
                'termsOfService': self.info_terms_of_service,
                'contact': {
                    'name': self.info_contact_name,
                    'url': self.info_contact_url,
                    'email': self.info_contact_email,
                },
                'license': {
                    'name': self.info_license_name,
                    'url': self.info_license_url
                }
            },
            'paths': self.__create_paths_data()
        }

        self._write_data(0, data)

        return self._content

    def __create_paths_data(self):
        data = {}
        for index in range(len(self.commands)):
            command = self.commands[index]

            path = self.base_route + '/' + command.get_name()
            if not path.startswith('/'):
                path = '/' + path
            data[path] = {
                'post': {
                    'tags': [self.base_route],
                    'operationId': command.get_name(),
                    'requestBody': self.__create_request_body_data(command),
                    'responses': self.__create_responses_data()
                }
            }

        return data

    def __create_request_body_data(self, command):
        schema_data = self.__create_schema_data(command)

        if schema_data is not None:
            return {
                'content': {
                    'application/json': {
                        'schema': schema_data
                    }
                }
            }

        return None

    def __create_schema_data(self, command):
        schema = command._schema

        if schema is None or schema.get_properties() is None:
            return None

        properties = {}
        required = []

        for property in schema.get_properties():
            properties[property.get_name()] = {
                'type': self._type_to_string(property.get_type())
            }
            if property.required:
                required.append(property.get_name())

        data = {
            'properties': properties
        }
        if len(required) > 0:
            data['required'] = required

        return data

    def __create_responses_data(self):
        return {
            '200': {
                'description': 'Successful response',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object'
                        }
                    }
                }
            }
        }

    def _write_data(self, indent, data: dict):
        for key, value in data.items():

            if isinstance(value, str):
                self._write_as_string(indent, key, value)

            elif isinstance(value, list):
                if len(value) > 0:
                    self._write_name(indent, key)
                    for index in range(len(value)):
                        item = value[index]
                        self._write_array_item(indent + 1, item)

            elif isinstance(value, dict):
                list_vals = list(value.values())
                try:
                    next(item for item in list_vals if item is not None)
                    self._write_name(indent, key)
                    self._write_data(indent + 1, value)
                except StopIteration:
                    pass
            else:
                self._write_as_object(indent, key, value)

    def _write_name(self, indent, name):
        spaces = self._get_spaces(indent)
        self._content += spaces + name + ":\n"

    def _write_array_item(self, indent, name, is_object_item=False):
        spaces = self._get_spaces(indent)
        self._content += spaces + '- '

        if is_object_item:
            self._content += name + ":\n"
        else:
            self._content += name + "\n"

    def _write_as_object(self, indent, name, value):
        if value is None:
            return
        spaces = self._get_spaces(indent)
        self._content += spaces + name + ": " + value + "\n"

    def _write_as_string(self, indent, name, value):
        if not value:
            return

        spaces = self._get_spaces(indent)
        self._content += spaces + name + ": '" + value + "'\n"

    def _get_spaces(self, length):
        return ' ' * length * 2

    def _type_to_string(self, type):
        # allowed types: array, boolean, integer, number, object, string
        if type == TypeCode.Integer or type == TypeCode.Long:
            return 'integer'
        if type == TypeCode.Double or type == TypeCode.Float:
            return 'number'
        if type == TypeCode.String:
            return 'string'
        if type == TypeCode.Boolean:
            return 'boolean'
        if type == TypeCode.Array:
            return 'array'
        return 'object'
