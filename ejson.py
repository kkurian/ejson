"""
EJSON is a complete implementation of EJSON according to Meteor version 0.6.

See README.md for details.

Homepage and documentation: https://github.com/kkurian/ejson

Copyright (c) 2013 Kerry Ivan Kurian
License: MIT (see LICENSE for details)
"""

__author__ = 'Kerry Ivan Kurian'
__version__ = '0.0'
__license__ = 'MIT'


import json
from time import mktime
from copy import deepcopy
from base64 import b64encode, b64decode
from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta
from json import JSONEncoder, JSONDecoder



class CustomType:
    __metaclass__ = ABCMeta

    @abstractmethod
    def clone(self):
        raise NotImplementedError

    @abstractmethod
    def equals(self, other):
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, other):
        raise NotImplementedError

    @abstractmethod
    def type_name(self):
        raise NotImplementedError

    @abstractmethod
    def to_json_value(self):
        raise NotImplementedError


class EJSONEncoder(JSONEncoder):
    _default = JSONEncoder.default

    def default(self, obj):
        if not isinstance(obj, CustomType):
            return super(EJSONEncoder, self).default(obj)
        return obj.to_json_value()


class EJSONDecoder(JSONDecoder):
    _custom_type_factories = dict()

    def __init__(self, encoding):
        super(EJSONDecoder, self).__init__(
            encoding, object_hook=EJSONDecoder.default)

    @classmethod
    def from_json_value(cls, val):
        try:
            key, value = val.iteritems().next()
            return cls._custom_type_factories[key](val)
        except (AttributeError, KeyError):
            # AttributeError means that val is not a dict and therefore not
            # a CustomType. KeyError means that no custom factory exists for
            # the val and therefore it is not a CustomType. In either case,
            # just return the val.
            return val

    @classmethod
    def register_custom_type(cls, custom_type_name, factory):
        if custom_type_name in cls._custom_type_factories:
            msg = 'name collision: custom type "{}" is already in use.'
            raise ValueError(msg.format(custom_type_name))
        cls._custom_type_factories[custom_type_name] = factory

    @classmethod
    def default(cls, dict_):
        if len(dict_) == 1 and \
                any(key in dict_ for key in cls._custom_type_factories):
            key, value = dict_.iteritems().next()
            return cls._custom_type_factories[key]({key: value})
        return dict_


def parse(str_):
    return loads(str_)


def loads(str_):
    return json.loads(str_, cls=EJSONDecoder)


def stringify(val):
    return dumps(val)


def dumps(val):
    return json.dumps(val, cls=EJSONEncoder)



def from_json_value(val):
    return EJSONDecoder.from_json_value(val)


def to_json_value(val):
    if isinstance(val, CustomType):
        return val.to_json_value()
    return val
    

def equals(a, b):
    if hasattr(a, '__eq__'):
        return a.__eq__(b)
    return _deep_eq(a, b)


def clone(val):
    return deepcopy(val)


# No need to def deepcopy(). See `from copy import deepcopy`, above.


def new_binary(size):
    return Binary(size)


def is_binary(x):
    return isinstance(x, Binary)


def add_type(name, factory):
    EJSONDecoder.register_custom_type(name, factory)



### Builtin CustomType's

DATE_TAG = '$date'
BINARY_TAG = '$binary'


# Date

class Date(datetime, CustomType):
    def clone(self):
        return deepcopy(self)

    def equals(self, other):
        return self.__eq__(other)

    # __eq__ is defined by datetime.

    def type_name(self):
        return DATE_TAG

    def to_json_value(self):
        msecs_since_epoch = \
            int(mktime(self.timetuple())*1e3 + self.microsecond/1e3)
        return {DATE_TAG: msecs_since_epoch}


def date_factory(json_dict):
    if len(json_dict) != 1:
        raise ValueError('Too many keys in {}.'.format(json_dict))

    try:
        timestamp = json_dict[DATE_TAG] / 1000.0 # milliseconds --> seconds
        return Date.fromtimestamp(timestamp)        
    except Exception as e:
        raise ValueError(e)


# Binary

class Binary(bytearray, CustomType):
    def clone(self):
        return deepcopy(self)

    def equals(self, other):
        return self.__eq__(other)

    # __eq__ is defined by datetime.

    def type_name(self):
        return BINARY_TAG

    def to_json_value(self):
        return {BINARY_TAG: b64encode(self)}


def binary_factory(json_dict):
    if len(json_dict) != 1:
        raise ValueError('Too many keys in {}.'.format(json_dict))

    try:
        return Binary(b64decode(json_dict[BINARY_TAG]))
    except Exception as e:
        return ValueError(e)


# Install Date and Binary
add_type(DATE_TAG, date_factory)
add_type(BINARY_TAG, binary_factory)

#
##

### Third-party code

##
# deep_eq
#
# From: https://gist.github.com/samuraisam/901117
#
# Copyright (c) 2010-2013 Samuel Sutch [samuel.sutch@gmail.com]
# License: MIT (see LICENSE for details)

_default_fudge = timedelta(seconds=0, microseconds=0, days=0)

def _deep_eq(_v1, _v2, datetime_fudge=_default_fudge, _assert=False):
  """
  Tests for deep equality between two python data structures recursing 
  into sub-structures if necessary. Works with all python types including
  iterators and generators. This function was dreampt up to test API responses
  but could be used for anything. Be careful. With deeply nested structures
  you may blow the stack.
  
  Options:
            datetime_fudge => this is a datetime.timedelta object which, when
                              comparing dates, will accept values that differ
                              by the number of seconds specified
            _assert        => passing yes for this will raise an assertion error
                              when values do not match, instead of returning 
                              false (very useful in combination with pdb)
  
  Doctests included:
  
  >>> x1, y1 = ({'a': 'b'}, {'a': 'b'})
  >>> deep_eq(x1, y1)
  True
  >>> x2, y2 = ({'a': 'b'}, {'b': 'a'})
  >>> deep_eq(x2, y2)
  False
  >>> x3, y3 = ({'a': {'b': 'c'}}, {'a': {'b': 'c'}})
  >>> deep_eq(x3, y3)
  True
  >>> x4, y4 = ({'c': 't', 'a': {'b': 'c'}}, {'a': {'b': 'n'}, 'c': 't'})
  >>> deep_eq(x4, y4)
  False
  >>> x5, y5 = ({'a': [1,2,3]}, {'a': [1,2,3]})
  >>> deep_eq(x5, y5)
  True
  >>> x6, y6 = ({'a': [1,'b',8]}, {'a': [2,'b',8]})
  >>> deep_eq(x6, y6)
  False
  >>> x7, y7 = ('a', 'a')
  >>> deep_eq(x7, y7)
  True
  >>> x8, y8 = (['p','n',['asdf']], ['p','n',['asdf']])
  >>> deep_eq(x8, y8)
  True
  >>> x9, y9 = (['p','n',['asdf',['omg']]], ['p', 'n', ['asdf',['nowai']]])
  >>> deep_eq(x9, y9)
  False
  >>> x10, y10 = (1, 2)
  >>> deep_eq(x10, y10)
  False
  >>> deep_eq((str(p) for p in xrange(10)), (str(p) for p in xrange(10)))
  True
  >>> str(deep_eq(range(4), range(4)))
  'True'  
  >>> deep_eq(xrange(100), xrange(100))
  True
  >>> deep_eq(xrange(2), xrange(5))
  False
  >>> import datetime
  >>> from datetime import datetime as dt
  >>> d1, d2 = (dt.now(), dt.now() + datetime.timedelta(seconds=4))
  >>> deep_eq(d1, d2)
  False
  >>> deep_eq(d1, d2, datetime_fudge=datetime.timedelta(seconds=5))
  True
  """
  _deep_eq = functools.partial(deep_eq, datetime_fudge=datetime_fudge, 
                               _assert=_assert)
  
  def _check_assert(R, a, b, reason=''):
    if _assert and not R:
      assert 0, "an assertion has failed in deep_eq (%s) %s != %s" % (
        reason, str(a), str(b))
    return R
  
  def _deep_dict_eq(d1, d2):
    k1, k2 = (sorted(d1.keys()), sorted(d2.keys()))
    if k1 != k2: # keys should be exactly equal
      return _check_assert(False, k1, k2, "keys")
    
    return _check_assert(operator.eq(sum(_deep_eq(d1[k], d2[k]) 
                                       for k in k1), 
                                     len(k1)), d1, d2, "dictionaries")
  
  def _deep_iter_eq(l1, l2):
    if len(l1) != len(l2):
      return _check_assert(False, l1, l2, "lengths")
    return _check_assert(operator.eq(sum(_deep_eq(v1, v2) 
                                      for v1, v2 in zip(l1, l2)), 
                                     len(l1)), l1, l2, "iterables")
  
  def op(a, b):
    _op = operator.eq
    if type(a) == datetime and type(b) == datetime:
      s = datetime_fudge.seconds
      t1, t2 = (mktime(a.timetuple()), mktime(b.timetuple()))
      l = t1 - t2
      l = -l if l > 0 else l
      return _check_assert((-s if s > 0 else s) <= l, a, b, "dates")
    return _check_assert(_op(a, b), a, b, "values")
 
  c1, c2 = (_v1, _v2)
  
  # guard against strings because they are iterable and their
  # elements yield iterables infinitely. 
  # I N C E P T I O N
  for t in types.StringTypes:
    if isinstance(_v1, t):
      break
  else:
    if isinstance(_v1, types.DictType):
      op = _deep_dict_eq
    else:
      try:
        c1, c2 = (list(iter(_v1)), list(iter(_v2)))
      except TypeError:
        c1, c2 = _v1, _v2
      else:
        op = _deep_iter_eq
  
  return op(c1, c2)

# End deep_eq
## 


if __name__ == '__main__':
    import doctest
    doctest.testmod()
