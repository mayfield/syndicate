syndicate - A wrapper for REST APIs
===========

Abstraction for HTTP based REST APIs;  Namely this is tested against tastypie
but should be adaptable to other API suites.


Requirements
========

* Requests


Installation
========

    python ./setup.py build
    python ./setup.py install


Compatibility
========

* Python 2.7
* Python 3.2+


Getting Started
========

**Example**

```python
import syndicate

basicauth = syndicate.BasicAuth('mrpresident', '1000xlight_points')
bakery = syndicate.Service(host='https://a.bakery.fake', urn='/api/v1/',
                           auth=basicauth)

# All the cake (includes paging support)...
for x in bakery.get('cake'):
    print("Cake is food:", x)

# Deletes
for x in bakery.get('cake', type='cheese'):
    print("Cheese is bad, deleting:", x)
    x.delete()

# Updates.
def = bakery.get('condiment', default=True)
if 'pepper' not in def['items']:
    def['items'].append('pepper')
    def.save()
else:
    print("We already serve pepper by default")

# Creation.
new_owl = bakery.post('cake', {
    "type": "chuck_norris",
    "name": "Round House",
    "scovilles": 16000000001  # sorry resiniferatoxin
}

# Subresources.
thing = bakery.get('thing', 100)
subthing = thing.fetch('subthing')
print("Subthing": subthing)

# Non-crud methods.
bakery.do('bake', 'cake', 100, temp=420, time=3600)
# Translates to
#   BAKE /api/v1/cake/100"
#   {"temp": 420, "time": 3600}
```
