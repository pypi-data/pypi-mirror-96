# -*- coding: utf-8 -*-
"""
    test.rest.DummyRestClient
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Dummy REST client implementation
    
    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from pip_services3_commons.data import DataPage

from pip_services3_rpc.clients import RestClient
from pip_services3_rpc.services import RestQueryParams
from .IDummyClient import IDummyClient


class DummyRestClient(RestClient, IDummyClient):

    def __init__(self):
        super(DummyRestClient, self).__init__()

    def get_page_by_filter(self, correlation_id, filters, paging):
        params = RestQueryParams(correlation_id, filters, paging)

        result = self.call(
            'GET',
            '/dummies',
            correlation_id,
            params
        )

        return DataPage(result['data'], result['total'])

    def get_one_by_id(self, correlation_id, id):
        return self.call(
            'GET',
            f'/dummies/{id}',
            correlation_id,
            {'id': id}
        )

    def create(self, correlation_id, entity):
        return self.call(
            'POST',
            '/dummies',
            correlation_id,
            None,
            {
                'body': entity
            }
        )

    def update(self, correlation_id, entity):
        return self.call(
            'PUT',
            '/dummies',
            correlation_id,
            None,
            {
                'body': entity
            }
        )

    def delete_by_id(self, correlation_id, id):
        return self.call(
            'DELETE',
            f'/dummies/{id}',
            correlation_id,
            {
                'dummy_id': id
            }
        )
