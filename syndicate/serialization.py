'''
Serialize data to/from foreign data types into python.
'''

from __future__ import print_function

import collections
import datetime
import json
import re

Serializer = collections.namedtuple('Serializer', 'mime, encode, decode')

ISO_DATE_RE = re.compile('(?P<dt>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})'
                         '(?P<utc_offset>[\-+]\d{2}:\d{2})')
ISO_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'


class NormalJSONEncoder(json.JSONEncoder):
    """ Normal == iso datatime.
    NOTE: Only UTC is supported."""

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime(ISO_DATE_FORMAT) + '+00:00'
        else:
            return super(NormalJSONEncoder, self).default(obj)


class NormalJSONDecoder(json.JSONDecoder):
    """ Normal == iso datatime.
    NOTE: Only UTC is supported."""

    def __init__(self):
        super(NormalJSONDecoder, self).__init__(object_hook=self.parse_object)

    def parse_object(self, data):
        """ Look for datetime looking strings. """
        for key, value in data.items():
            try:
                value = ISO_DATE_RE.match(value).groupdict()
                dt = datetime.datetime.strptime(value['dt'], ISO_DATE_FORMAT)
            except (AttributeError, TypeError, ValueError):
                pass
            else:
                hours, mins = map(int, value['utc_offset'].split(':'))
                if hours < 0:
                    mins *= -1
                if hours:
                    dt -= datetime.timedelta(hours=hours+(mins/60))
                data[key] = dt
        return data

serializers = {
    'json': Serializer('application/json',
                       NormalJSONEncoder().encode,
                       NormalJSONDecoder().decode)
}
