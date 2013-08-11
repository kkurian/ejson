Meteor's EJSON for Python 2.7
=============================

*THIS IS A WORK IN PROGRESS THAT IS NOT CURRENTLY FUNCTIONAL.*

  [ddp]: http://docs.meteor.com/#ejson

This is a complete implementation, for Python 2.7, of EJSON as specified in
version 0.6.4 the Meteor documentation, found [here][ddp].

The EJSON specification assumes JavaScript, so this version deviates from the
specification as follows:

* Pythonic naming of methods (e.g., `from_json_value` instead of `fromJSONValue`)
* aliases where more natural Python method names exist (e.g., `dumps` is aliased to `stringify`).
* Python data types in place of the specified JavaScript data types (e.g., `bytearray` instead of `Uint8Array`).
* virtual base class for user defined datatypes: `ejson.CustomType`

Want this to be Python 3 compatible? Send pull requests! :)


EJSON
-----

EJSON is an extension of JSON to support more types. It supports all JSON-safe
types, as well as:

* Date (Python `datetime` with `ejson.CustomType` mixin)
* Binary (Python `bytearray` with `ejson.CustomType` mixin)
* User-defined types (see `ejson.add_type`)

All EJSON serializations are also valid JSON. For example an object with a
date and a binary buffer would be serialized in EJSON as:

	{
	  "d": {"$date": 1358205756553},
	  "b": {"$binary": "c3VyZS4="}
	}

### ejson.parse(str), ejson.loads(str)

Parse a string into an EJSON value. Throws an error if the string is not valid
ejson.

`str` (str)<br/>
A string to parse into an EJSON value.


### ejson.stringify(val), ejson.dumps(val)

Serialize a value to a string.

For EJSON values, the serialization fully represents the value. For non-EJSON
values, serializes the same way as `json.dumps`.

`val` (EJSON-compatible value)<br/>
A value to stringify.


### ejson.from\_json\_value(val)

Deserialize an EJSON value from its plain JSON representation.

`val` (JSON-compatible value)<br/>
A value to deserialize into ejson.


### ejson.to\_json\_value(val)

Serialize an EJSON-compatible value into its plain JSON representation.

`val` (EJSON-compatible value)<br/>
A value to serialize to plain JSON.


### ejson.equals(a, b)

Return `True` if `a` and `b` are equal to each other. Return `False`
otherwise. Uses the `__eq__` method on `a` if present, otherwise performs a
deep comparison.

`a` (EJSON-compatible object)<br/>
`b` (EJSON-compatible object)


### ejson.clone(val), ejson.deepcopy(val)

Return a deep copy of val.

`val` (EJSON-compatible value)<br/>
A value to copy.


### ejson.new_binary(size)

Allocate a new buffer of binary data that EJSON can serialize.

`size` (int)<br/>
The number of bytes of binary data to allocate.

Buffers of binary data are represented by `bytearray` instances containing
numbers ranging from 0 to 255.


### ejson.is_binary(x)

Returns `True` if `x` is a buffer of binary data, as returned from
`ejson.new_binary`. Otherwise, returns `False`.


### ejson.add_type(name, factory)

Add a custom datatype to EJSON.

Raises `ValueError` if `name` is not unique among custom data types
defined in your project.

`name` (String)<br/>
A tag for your custom type (e.g., `'$my_type'`); must be unique among custom data types defined in
your project, and must match the result of your type's `type_name` method.

`factory` (function)<br/>
A function that converts a JSON-compatible `dict` (something like `{"$my_type":
"some value"}`) into an instance of your type. This should be the inverse of
the serialization performed by your type's `to_json_value` method. Your
factory must raise `ValueError` if it cannot process the value it receives.

*Instances of your custom datatype must inheret and implement
`ejson.CustomType`, which is a virtual base class.*

### ejson.CustomType

#### ejson.CustomType.clone()

Return a value `r` such that `r.__eq__(r)` is always `True`, even if `r` is
later modified.


#### ejson.CustomType.equals(other), instance.\_\_eq\_\_(other)

> You must define both `equals(other)` and `__eq__(other)`, with one being
> an alias for the other.

Return `True` if `other` has a value equal to `self`; `False` otherwise.

`other` (object)<br/>
The object to which to compare `self`.

The equals method should define an equivalence relation. It should have the
following properties:

* Reflexivity - for any instance `a`: `a.equals(a)` must be `True`.
* Symmetry - for any two instances `a` and `b`: `a.equals(b)` if and only if `b.equals(a)`.
* Transitivity - for any three instances `a`, `b`, and `c`: `a.equals(b)` and `b.equals(c)` implies `a.equals(c)`.

#### ejson.CustomType.type_name

Return the tag used to identify this type. This must match the tag used to
register this type with `ejson.add_type`. Something like `'$my_type'`.

#### ejson.CustomType.to\_json\_value()

Serialize this instance into a JSON-compatible `dict`. Something like
`{"$my_type": "some value"}`.
