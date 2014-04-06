"""
Sanity tests for the syndicate library.
"""

from __future__ import print_function, division

import datetime
import syndicate
import unittest

class BaseTest(unittest.TestCase):

    def test_service_construct(self):
        self.assertRaises(TypeError, syndicate.Service)
        syndicate.Service(host='foo', urn='bar')

    def test_json_serializer(self):
        input_ = {
            "duck": {
                "talk": "Quack!",
                "walk": 0.001,
                "is_duck": True,
                "born": datetime.datetime.utcnow()
            }
        }
        data = syndicate.serializers['json'].encode(input_)
        output = syndicate.serializers['json'].decode(data)
        self.assertEqual(input_, output)
