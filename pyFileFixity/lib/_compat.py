#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

try: # compatibility with Python 3+
    _range = xrange
except NameError:
    _range = range

try:
    from cStringIO import StringIO
    _StringIO = StringIO
except (ImportError, NameError): #python3.x
    from io import StringIO
    _StringIO = StringIO

try:
    from itertools import izip
    _izip = izip
except ImportError:  #python3.x
    _izip = zip

try:
    _str = basestring
except NameError:
    _str = str

if sys.version_info < (3,):
    def b(x):
        return x
else:
    import codecs
    def b(x):
        if isinstance(x, _str):
            return codecs.latin_1_encode(x)[0]
        else:
            return x

if sys.version_info < (3,):
    def _open_csv(x, mode='r'):
        return open(x, mode+'b')
else:
    def _open_csv(x, mode='r'):
        return open(x, mode+'t', newline='')
