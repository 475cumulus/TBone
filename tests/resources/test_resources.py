#!/usr/bin/env python
# encoding: utf-8

import pytest
from tbone.testing.clients import *
from tbone.testing.fixtures import json_fixture
from .resources import *


async def get_total_count(client, url):
    ''' Utility method to get the total count of a resource'''
    response = await client.get(url=url)
    assert isinstance(response, Response)
    assert response.status == OK
    # parse response and retrieve data
    data = client.parse_response_data(response)
    assert 'meta' in data
    return data['meta'].get('total_count')


@pytest.mark.asyncio
async def test_resource_get_list(event_loop, json_fixture):
    # load datafixture for this test
    app = App(db=json_fixture('persons.json'))
    # set variables
    limit = 22
    url = '/api/{}/'.format(PersonResource.__name__)
    client = ResourceTestClient(app, PersonResource)

    response = await client.get(url=url, args={'limit': limit})
    # make sure we got a response object
    assert isinstance(response, Response)
    # parse response and retrieve data
    data = client.parse_response_data(response)
    assert 'meta' in data
    assert 'objects' in data
    assert len(data['objects']) == limit


@pytest.mark.asyncio
async def test_resource_get_detail(event_loop, json_fixture):
    # load datafixture for this test
    app = App(db=json_fixture('persons.json'))
    # set variables
    id = 13
    url = '/api/{}/{}/'.format(PersonResource.__name__, id)
    client = ResourceTestClient(app, PersonResource)

    response = await client.get(url=url)
    # make sure we got a response object
    assert isinstance(response, Response)
    # parse response and retrieve data
    obj = client.parse_response_data(response)
    assert 'error' not in obj
    # check that id matches
    assert obj['id'] == id
    # check all expected keys are in
    assert set(('id', 'first_name', 'last_name', '_links')) == set(obj.keys())


@pytest.mark.asyncio
async def test_resource_post(event_loop, json_fixture):
    # load datafixture for this test
    app = App(db=json_fixture('persons.json'))
    # set variables
    url = '/api/{}/'.format(PersonResource.__name__)
    client = ResourceTestClient(app, PersonResource)

    # get the count before insertion
    count1 = await get_total_count(client, url)

    # send a POST request to create a new Person
    response = await client.post(url=url, body={
        'id': count1 + 1,
        'first_name': 'Ron',
        'last_name': 'Burgundy',
    })
    assert isinstance(response, Response)
    # parse response and retrieve data
    obj = client.parse_response_data(response)
    assert 'error' not in obj

    # get the count after insertion
    count2 = await get_total_count(client, url)
    assert count1 + 1 == count2


@pytest.mark.asyncio
async def test_resource_update(event_loop, json_fixture):
    # load datafixture for this test
    app = App(db=json_fixture('persons.json'))
    # set variables


@pytest.mark.asyncio
async def test_resource_delete(event_loop, json_fixture):
    # load datafixture for this test
    app = App(db=json_fixture('persons.json'))
    # set variables


@pytest.mark.asyncio
async def test_resource_hateoas(event_loop, json_fixture):
    def _check(obj):
        assert '_links' in obj
        assert 'self' in obj['_links']
        assert 'href' in obj['_links']['self']
        assert url in obj['_links']['self']['href']

    # load datafixture for this test
    app = App(db=json_fixture('persons.json'))
    # set variables
    url = '/api/{}/'.format(PersonResource.__name__)
    client = ResourceTestClient(app, PersonResource)

    # get collection of persons
    response = await client.get(url=url)
    assert isinstance(response, Response)
    assert response.status == OK
    # parse response and retrieve data
    data = client.parse_response_data(response)
    for resource in data['objects']:
        _check(resource)

    # test on single resource
    href = data['objects'][0]['_links']['self']['href']
    response = await client.get(url=href)
    assert isinstance(response, Response)
    assert response.status == OK
    resource = client.parse_response_data(response)
    _check(resource)


@pytest.mark.asyncio
async def test_resource_without_hateoas(event_loop, json_fixture):
    # load datafixture for this test
    app = App(db=json_fixture('persons.json'))
    # turn off hypermedia

    class NoHPersonResource(PersonResource):
        class Meta:
            hypermedia = False

    url = '/api/{}/'.format(NoHPersonResource.__name__)
    client = ResourceTestClient(app, NoHPersonResource)
    # get collection of persons
    response = await client.get(url=url)
    assert isinstance(response, Response)
    assert response.status == OK
    # parse response and retrieve data
    data = client.parse_response_data(response)
    for resource in data['objects']:
        assert '_links' not in resource
