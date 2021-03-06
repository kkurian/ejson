"""
Copyright (C) 2013 Kerry Ivan Kurian.
License: MIT (see LICENSE for details)
"""

from copy import deepcopy
from random import choice
from datetime import timedelta

import pytest

import ejson


MS_SINCE_EPOCH = 1358205756553


ejsonobj_string_pairs = [
    (
        # EJSON Date
        ejson.Date.fromtimestamp(MS_SINCE_EPOCH/1000.0),
        ''.join(['{"$date": ', str(MS_SINCE_EPOCH), '}'])
    ), (
        # EJSON Binary
        ejson.Binary(b'sure.'),
        '{"$binary": "c3VyZS4="}'
    )
]

json_string_pairs = [
    (
        # Regular JSON
        {'foo': 'bar'},
        '{"foo": "bar"}'
    )
]

ejsonobj_json_pairs = [
    (
        # EJSON Date
        ejson.Date.fromtimestamp(MS_SINCE_EPOCH/1000.0),
        {"$date": MS_SINCE_EPOCH}
    ), (
        # EJSON Binary
        ejson.Binary(b'sure.'),
        {"$binary": "c3VyZS4="}
    )
]

json_json_pairs = [
    (
        # Regular JSON
        {'foo': 'bar'},
        {"foo": "bar"}
    )
]


## Test Date and Binary
def _assert_serialize_deserialize_equals_and_is_binary(
    ejson_obj, json_obj, json_str, is_binary
):
    assert json_str == ejson.stringify(ejson_obj)
    assert json_str == ejson.dumps(ejson_obj)
    assert json_obj == ejson.to_json_value(ejson_obj)

    assert ejson_obj == ejson.parse(json_str)
    assert ejson_obj == ejson.loads(json_str)
    assert ejson_obj == ejson.from_json_value(json_obj)

    ejson_obj2 = deepcopy(ejson_obj)

    assert ejson.equals(ejson_obj, ejson_obj2)
    assert ejson.equals(ejson_obj, ejson.clone(ejson_obj))
    assert is_binary == ejson.is_binary(ejson_obj)


def test_date():
    ejson_obj = ejson.Date.fromtimestamp(MS_SINCE_EPOCH/1000.0)
    json_obj = {'$date': MS_SINCE_EPOCH}
    json_str = '{"$date": ' + str(MS_SINCE_EPOCH) + '}'

    _assert_serialize_deserialize_equals_and_is_binary(
        ejson_obj, json_obj, json_str, False)


def test_binary():
    ejson_obj = ejson.new_binary(5)

    assert isinstance(ejson_obj, bytearray)
    assert len(ejson_obj) == 5

    ejson_obj[:] = b'sure.'
    json_obj = {'$binary': "c3VyZS4="}
    json_str = '{"$binary": "c3VyZS4="}'

    _assert_serialize_deserialize_equals_and_is_binary(
        ejson_obj, json_obj, json_str, True)
##


## Test Parse and Loads
def _parse_test(method):
    ms = str(MS_SINCE_EPOCH)
    json_str = '[{"$binary": "c3VyZS4="}, {"$date": ' + ms + '}, {"a": true}]'

    obj = method(json_str)
    
    assert obj[0] == ejson.Binary(b'sure.')
    assert obj[1] == ejson.Date.fromtimestamp(MS_SINCE_EPOCH/1e3)
    assert obj[2] == {'a': True}

def test_parse():
    _parse_test(ejson.parse)

def test_loads():
    _parse_test(ejson.loads)
##



@pytest.mark.parametrize(
    ('ejsonobj', 'string'),
    ejsonobj_string_pairs + json_string_pairs
)
def test_stringify_and_dumps(ejsonobj, string):
    assert string == ejson.stringify(ejsonobj)
    assert string == ejson.dumps(ejsonobj)


@pytest.mark.parametrize(
    ('ejsonobj', 'json'),
    ejsonobj_json_pairs + json_json_pairs
)
def test_from_json_value(ejsonobj, json):
    assert ejsonobj == ejson.from_json_value(json)


@pytest.mark.parametrize(
    ('ejsonobj', 'json'),
    ejsonobj_json_pairs + json_json_pairs
)
def test_to_json_value(ejsonobj, json):
    assert json == ejson.to_json_value(ejsonobj)


@pytest.mark.parametrize(
    ('ejsonobj', 'json'),
    ejsonobj_json_pairs + json_json_pairs
)
def test_equals_and_eq(ejsonobj, json):
    ejsonobj_copy = deepcopy(ejsonobj)
    ejsonobj_copy_2 = deepcopy(ejsonobj_copy)

    # Reflexivity
    assert ejson.equals(ejsonobj, ejsonobj)

    # Symmetry
    assert ejson.equals(ejsonobj, ejsonobj_copy)
    assert ejson.equals(ejsonobj_copy, ejsonobj)

    # Transivity
    assert ejson.equals(ejsonobj, ejsonobj_copy)
    assert ejson.equals(ejsonobj_copy, ejsonobj_copy_2)
    assert ejson.equals(ejsonobj, ejsonobj_copy_2)


@pytest.mark.parametrize(
    ('ejsonobj', 'json'),
    ejsonobj_json_pairs + json_json_pairs
)
def test_clone(ejsonobj, json):
    clone = ejson.clone(ejsonobj)

    assert clone == ejsonobj

    # clone() must return a value r such that r.__eq__(r) is always True,
    # even if r is later modified.
    if isinstance(ejsonobj, ejson.Date):
        ejsonobj += timedelta(hours=1)        
    elif isinstance(ejsonobj, ejson.Binary):
        ejsonobj[:0] = b'x'
    elif isinstance(ejsonobj, dict): # is JSON object
        # Change the value of the first key.
        assert ejsonobj[ejsonobj.keys()[0]] != 'x'
        ejsonobj[ejsonobj.keys()[0]] = 'x'
    else:
        assert False # You need to implement this for your new type.

    assert clone == clone
    assert clone != ejsonobj


def test_new_binary():
    obj = ejson.new_binary(8)
    assert isinstance(obj, bytearray)
    assert 8 == len(obj)


def test_is_binary():
    assert ejson.is_binary(ejson.new_binary(1))
    assert not ejson.is_binary('foo')


##
#
def _bad_factory(json):
    # BadObject is bad because it does not inherit from ejson.CustomType.
    class BadObject(object): pass
    return BadObject()

def test_add_type():
    # The EJSON Date and Binary types are themselves implemented using
    # add_type(). If the foregoing tests pass, it demonstrates that add_type()
    # is working.

    # Now, Try to break add_type().

    # Add a types that already exists.
    pytest.raises(ValueError, "ejson.add_type('$date', _bad_factory)")
    pytest.raises(ValueError, "ejson.add_type('$binary', _bad_factory)")
