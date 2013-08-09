"""
Copyright (C) 2013 Kerry Ivan Kurian.
License: MIT (see LICENSE for details)
"""

from copy import deepcopy
from random import choice
from datetime import datetime

import pytest

import ejson


MS_SINCE_EPOCH = 1358205756553

##
# Test Date and Binary

def _assert_serialize_deserialize_equals_and_is_binary(
    ejson_obj, json, is_binary
):
    assert json == ejson.stringify(ejson_obj)
    assert json == ejson.dumps(ejson_obj)
    assert json == ejson.to_json_value(ejson_obj)

    assert ejson_obj == ejson.parse(json)
    assert ejson_obj == ejson.loads(json)
    assert ejson_obj == ejson.from_json_value(json)

    ejson_obj2 = deepcopy(ejson_obj)

    assert ejson.equals(obj, ejson_obj2)
    assert ejson.equals(obj, ejson.clone(obj))
    assert is_binary == ejson.is_binary(obj)

def test_date():
    ejson_obj = {'$date': datetime.fromtimestamp(MS_SINCE_EPOCH/1000.0)}
    json = '{"$date": ' + str(MS_SINCE_EPOCH) + '}'

    _assert_serialize_deserialize_equals_and_is_binary(ejson_obj, json, False)


def test_binary():
    obj = ejson.new_binary(5)

    assert isinstance(obj, bytearray)
    assert len(obj) == 5

    obj[:] = b'sure.'
    obj_json = '{"$binary": "c3VyZS4="}'

    _assert_serialize_deserialize_equals_and_is_binary(ejson_obj, json, True)
#
##


##
# Test Parse and Loads

def _parse_test(method):
    obj_json = ''.join([
        '{"$binary": "c3VyZS4="}, {"$date": ', MS_SINCE_EPOCH, '}, "a": true}'
    ])
    obj = method(obj_json)

    assert len(obj) == 3
    for key, value in [
        ('$binary', bytearray(b'sure.')),
        ('$date', datetime.fromtimestamp(MS_SINCE_EPOCH/1000.0)),
        ('a', True)
    ]:
        assert obj[key] == value

def test_parse():
    _parse_test(ejson.parse)

def test_loads():
    _parse_test(ejson.loads)
#
##


parameters = [
    (
        # EJSON Date
        {'$date': datetime.fromtimestamp(MS_SINCE_EPOCH/1000.0)},
        ''.join(['{"$date": ', str(MS_SINCE_EPOCH), '}'])
    ), (
        # EJSON Binary
        {'$binary': bytearray(b'sure.')},
        '{"$binary": "c3VyZS4="}'
    ), (
        # Regular JSON
        {'foo': 'bar'},
        '{"foo": "bar"}'
    )
]


@pytest.mark.parametrize(('ejson_obj', 'json'), parameters)
def test_stringify_and_dumps(ejson_obj, json):
    assert json == ejson.stringify(ejson_obj)
    assert json == ejson.dumps(ejson_obj)


@pytest.mark.parametrize(('ejson_obj', 'json'), parameters)
def test_from_json_value(ejson_obj, json):
    assert ejson_obj == ejson.from_json_value(json)


@pytest.mark.parametrize(('ejson_obj', 'json'), parameters)
def test_to_json_value(ejson_obj, json):
    assert json == ejson.to_json_value(ejson_obj)


@pytest.mark.parametrize(('ejson_obj', 'json'), parameters)
def test_equals_and_eq(ejson_obj, json):
    ejson_obj_copy = deepcopy(ejson_obj)
    ejson_obj_copy_2 = deepcopy(ejson_obj_copy)

    # Reflexivity
    assert ejson.equals(ejson_obj, ejson_obj)

    # Symmetry
    assert ejson.equals(ejson_obj, ejson_obj_copy)
    assert ejson.equals(ejson_obj_copy, ejson_obj)

    # Transivity
    assert ejson.equals(ejson_obj, ejson_obj_copy)
    assert ejson.equals(ejson_obj_copy, ejson_obj_copy_2)
    assert ejson.equals(ejson_obj, ejson_obj_copy_2)


@pytest.mark.parametrize(('ejson_obj', 'json'), parameters)
def test_clone(ejson_obj, json):
    clone = ejson.clone(ejson_obj)

    assert clone == ejson_obj

    # clone() must return a value r such that r.__eq__(r) is always True,
    # even if r is later modified.
    clone[clone.keys()[0]] = 'blarghz'
    assert clone == clone

    assert clone != ejson_obj


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

    # 1. Add a type that already exists.
    pytest.raises(ValueError, "ejson.add_type('date', _bad_factory)")
    pytest.raises(ValueError, "ejson.add_type('binary', _bad_factory)")

    # 2. Add a factory that returns objects that do not implement the
    # required interface.
    ejson.add_type('bad', _bad_factory)
    pytest.raises(
        ejson.BadFactory,
        lambda: ejson.from_json_value("{$bad': 'foo'}")
    )
