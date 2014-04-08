'''
Serialize data to/from foreign data types into python.
'''

from __future__ import print_function

import collections
import datetime
import dateutil.parser
import json

Serializer = collections.namedtuple('Serializer', 'mime, encode, decode')


class DictResponse(dict):
    pass


class ListResponse(list):
    pass


class NormalJSONEncoder(json.JSONEncoder):
    """ Normal == iso datatime. """

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        else:
            return super(NormalJSONEncoder, self).default(obj)


class NormalJSONDecoder(json.JSONDecoder):
    """ Normal == iso datatime. """

    def __init__(self):
        super(NormalJSONDecoder, self).__init__(object_hook=self.parse_object)

    def parse_object(self, data):
        """ Look for datetime looking strings. """
        for key, value in data.items():
            try:
                # XXX Too open.
                data[key] = dateutil.parser.parse(value)
            except (AttributeError, TypeError, ValueError):
                pass
        return data

serializers = {
    'json': Serializer('application/json',
                       NormalJSONEncoder().encode,
                       NormalJSONDecoder().decode)
}
