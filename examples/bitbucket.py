import syndicate
from syndicate.client import ResponseError


def bb_data_getter(response):
    if response.error:
        # Simply push up the http code instead of any serialization issues.
        raise ResponseError("HTTP Code: %d" % response.http_code)
    return response.content

bb = syndicate.Service(uri="https://bitbucket.org", urn="/api/1.0/",
                       data_getter=bb_data_getter,
                       auth=("justinmayfield", "********"))

try:
    bb.get("users")
except ResponseError as e:
    print('Good Fail:', e)

print("Good Success", bb.get("users", "justinmayfield"))
print("Good Success", bb.get("users", "justinmayfield", "plan"))
print("Good Success", bb.get("user"))
