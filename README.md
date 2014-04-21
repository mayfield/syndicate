syndicate - A wrapper for REST APIs
===========

Abstraction for HTTP based REST APIs;  Namely this is tested against tastypie
but should be adaptable to other API suites.


Requirements
========

* Requests (sync mode)
* Tornado (async mode)


Installation
========

    python ./setup.py build
    python ./setup.py install


Compatibility
========

* Python 2.7
* Python 3.2+


TODO
========

* Unified authentication between HTTP adapters.
* PUT, POST, DELETE Support
* Documentation


Getting Started
========

**Example (Syncronous mode - using requests)**

```python
import syndicate

bakery = syndicate.Service(uri='https://a.bakery.fake', urn='/api/v1/',
                           auth=('mrpresident', '1000xlight_points'))

for x in bakery.get('cake'):
    print("Cake is food:", x)

# Deletes
for x in bakery.get('cake', type='cheese'):
    print("Cheese is bad, deleting:", x)
    x.delete()

# Updates.
default = bakery.get('condiment', default=True)
if 'pepper' not in def['items']:
    default['items'].append('pepper')
    default.save()
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


**Example (Asyncronous mode - using tornado)**
```python
import syndicate

bakery = syndicate.Service(uri='https://a.bakery.fake', urn='/api/v1/',
                           auth=('mrpresident', '1000xlight_points'),
                           async=True)

# Using future objects...
future_result = bakery.get('cake')

def handle_response(f):
    for x in f.result():
        print("Cake is food:", x)

future_result.add_done_callback(handle_response)

# As a convience you can set the callback on the request...
def handle_response(f):
    for x in f.result():
        print("Cake is food:", x)

bakery.get('cake', callback=handle_response)
```
