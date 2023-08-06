#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Basic JS types tests """

import unittest
import json
import time

from datetime import datetime

from py_mini_racer import py_mini_racer


class Test(unittest.TestCase):
    """ Test basic types """

    def valid(self, py_val, **kwargs):
        if 'testee' in kwargs:
            testee = kwargs['testee']
        else:
            testee = py_val
        js_str = json.dumps(py_val)
        parsed = self.mr.execute(js_str)
        self.assertEqual(testee, parsed)

    def setUp(self):

        self.mr = py_mini_racer.MiniRacer()

    def test_str(self):
        self.valid("'a string'")
        self.valid("'a ' + 'string'")

    def test_unicode(self):
        ustr = u"\N{GREEK CAPITAL LETTER DELTA}"
        res = self.mr.eval("'" + ustr + "'")
        self.assertEqual(ustr, res)

    def test_numbers(self):
        self.valid(1)
        self.valid(1.0)
        self.valid(2**16)
        self.valid(2**31-1)
        self.valid(2**31)
        self.valid(2**33)

    def test_arrays(self):
        self.valid([1])
        self.valid([])
        self.valid([1, 2, 3])
        # Nested
        self.valid([1, 2, ['a', 1]])

    def test_none(self):
        self.valid(None)

    def test_hash(self):
        self.valid({})
        self.valid('{}')
        self.valid({'a': 1})
        self.valid({" ": {'z': 'www'}})

    def test_complex(self):

        self.valid({
            1: [
                1, 2, 'qwe', {
                    'z': [
                        4, 5, 6, {
                            'eqewr': 1,
                            'zxczxc': 'qweqwe',
                            'z': {1: 2}
                        }
                    ]
                }
            ], 'qwe': 1
        })

    def test_function(self):
        res = self.mr.eval('var a = function(){}; a')
        self.assertTrue(isinstance(res, py_mini_racer.JSFunction))

    def test_invalid_key(self):

        fun = """
            var o = {};
            o.__defineGetter__("bar", function() { return null(); });
            o
        """
        with self.assertRaises(py_mini_racer.JSConversionException):
            self.mr.eval(fun)

    def test_timestamp(self):
        val = int(time.time())
        res = self.mr.eval("var a = new Date(%d); a" % (val * 1000))
        self.assertEqual(res, datetime.utcfromtimestamp(val))

    def test_date(self):
        res = self.mr.eval("var a = new Date(Date.UTC(2014, 0, 2, 3, 4, 5)); a")
        self.assertEqual(res, datetime(2014, 1, 2, 3, 4, 5))

    def test_exception(self):
        js_source = """
        var f = function(arg) {
            throw 'error: '+arg
            return nil
        }"""

        self.mr.eval(js_source)

        with self.assertRaises(py_mini_racer.JSEvalException) as cm:
            self.mr.eval("f(42)")

        self.assertIn('error: 42', cm.exception.args[0])


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
