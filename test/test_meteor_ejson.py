"""
Here are Meteor's own ejson_test.js translated into Python.

Copyright (C) 2013 Kerry Ivan Kurian.
License: MIT (see LICENSE for details)

Based upon:
url: https://github.com/meteor/meteor/blob/master/packages/ejson/ejson_test.js
commit: 9bb2b5447e845c4f483df5e9b42a2c1de5ab909b
"""

import pytest
import ejson

def test_key_order_sensitive():
    # Tinytest.add("ejson - keyOrderSensitive", function (test) {
    #   test.isTrue(EJSON.equals({
    #     a: {b: 1, c: 2},
    #     d: {e: 3, f: 4}
    #   }, {
    #     d: {f: 4, e: 3},
    #     a: {c: 2, b: 1}
    #   }));
    obj = ejson.loads('{"a": {"b": 1, "c": 2}, "d": {"e": 3, "f": 4}}')
    obj2 = ejson.loads('{"d": {"f": 4, "e": 3}, "a": {"c": 2, "b": 1}}')
    assert ejson.equals(obj, obj2)

    #   test.isFalse(EJSON.equals({
    #     a: {b: 1, c: 2},
    #     d: {e: 3, f: 4}
    #   }, {
    #     d: {f: 4, e: 3},
    #     a: {c: 2, b: 1}
    #   }, {keyOrderSensitive: true}));
    assert not ejson.equals(obj, obj2, key_order_sensitive=True)
    
    #   test.isFalse(EJSON.equals({
    #     a: {b: 1, c: 2},
    #     d: {e: 3, f: 4}
    #   }, {
    #     a: {c: 2, b: 1},
    #     d: {f: 4, e: 3}
    #   }, {keyOrderSensitive: true}));
    obj = ejson.loads('{"a": {"b": 1, "c": 2}, "d": {"e": 3, "f": 4}}')
    obj2 = ejson.loads('{"a": {"c": 2, "b": 1}, "d": {"f": 4, "e": 3}}')
    assert not ejson.equals(obj, obj2, key_order_sensitive=True)

    #   test.isFalse(EJSON.equals({a: {}}, {a: {b:2}}, {keyOrderSensitive: true}));
    obj = ejson.loads('{"a": {}}')
    obj2 = ejson.loads('{"a": {"b":2}}')
    assert not ejson.equals(obj, obj2, key_order_sensitive=True)

    #   test.isFalse(EJSON.equals({a: {b:2}}, {a: {}}, {keyOrderSensitive: true}));
    assert not ejson.equals(obj2, obj, key_order_sensitive=True)    

    # });
    
# Tinytest.add("ejson - nesting and literal", function (test) {
#   var d = new Date;
#   var obj = {$date: d};
#   var eObj = EJSON.toJSONValue(obj);
#   var roundTrip = EJSON.fromJSONValue(eObj);
#   test.equal(obj, roundTrip);
# });

# Tinytest.add("ejson - some equality tests", function (test) {
#   test.isTrue(EJSON.equals({a: 1, b: 2, c: 3}, {a: 1, c: 3, b: 2}));
#   test.isFalse(EJSON.equals({a: 1, b: 2}, {a: 1, c: 3, b: 2}));
#   test.isFalse(EJSON.equals({a: 1, b: 2, c: 3}, {a: 1, b: 2}));
#   test.isFalse(EJSON.equals({a: 1, b: 2, c: 3}, {a: 1, c: 3, b: 4}));
#   test.isFalse(EJSON.equals({a: {}}, {a: {b:2}}));
#   test.isFalse(EJSON.equals({a: {b:2}}, {a: {}}));
# });

# Tinytest.add("ejson - equality and falsiness", function (test) {
#   test.isTrue(EJSON.equals(null, null));
#   test.isTrue(EJSON.equals(undefined, undefined));
#   test.isFalse(EJSON.equals({foo: "foo"}, null));
#   test.isFalse(EJSON.equals(null, {foo: "foo"}));
#   test.isFalse(EJSON.equals(undefined, {foo: "foo"}));
#   test.isFalse(EJSON.equals({foo: "foo"}, undefined));
# });

# Tinytest.add("ejson - clone", function (test) {
#   var cloneTest = function (x, identical) {
#     var y = EJSON.clone(x);
#     test.isTrue(EJSON.equals(x, y));
#     test.equal(x === y, !!identical);
#   };
#   cloneTest(null, true);
#   cloneTest(undefined, true);
#   cloneTest(42, true);
#   cloneTest("asdf", true);
#   cloneTest([1, 2, 3]);
#   cloneTest([1, "fasdf", {foo: 42}]);
#   cloneTest({x: 42, y: "asdf"});

#   var testCloneArgs = function (/*arguments*/) {
#     var clonedArgs = EJSON.clone(arguments);
#     test.equal(clonedArgs, [1, 2, "foo", [4]]);
#   };
#   testCloneArgs(1, 2, "foo", [4]);
# });