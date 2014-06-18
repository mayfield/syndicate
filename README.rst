syndicate - A wrapper for REST APIs
===========

Abstraction for HTTP based REST APIs.  This provides a means to generically
handle serialization (JSON) and URI mapping as seen in many of the REST APIs
published these days.  Currently Tastypie APIs are the primary target but the
system should be compossible enough to work with other APIs if they work
roughly the same way. 


Requirements
--------

* Requests (sync mode)
* Tornado (async mode)


Installation
--------

    python ./setup.py build
    python ./setup.py install


Compatibility
--------

* Python 2.7
* Python 3.3+


TODO
--------

* Unified authentication between HTTP adapters.
* Documentation


Getting Started
--------

Syndicate has two basic modes for communicating with an API, sync and async.
The sync mode uses the 'requests' library as the HTTP adapter and the async
mode uses the 'tornado' web framework.  An adapter can be provided by the
user if they have their own backend to use too;  Twisted for example.

In either mode, your interface is a 'Service' instance, which facilitates
authentication, session management (via an adapter) and serialization.


Synchronous Examples
--------

**Creating a connnection**

Instantiate a service class with some basic descriptions of the remote API
to get a persistent connection.

```python
import syndicate

bakery = syndicate.Service(uri='https://a.bakery.fake', urn='/api/v1/',
                           auth=('mrpresident', '1000xlight_points'))
```


**Simple GET**

Fetch all the resources at https://a.bakery.fake/api/v1/cake/

```python
for x in bakery.get('cake'):
    print("Cake is food:", x)
```


**Delete with filter**

Keyword arguments are converted to URL queries.  To filter by an exact
field match such as https://a.bakery.fake/api/v1/cake/?type=cheese we
simply add the 'type' keyword to the <verb>() call.  This example deletes
all cheese cakes because I hate cheese.

```python
for x in bakery.get('cake', type='cheese'):
    x.delete()
```


**Update a resource**

Resources implement the mapping protocol so they work like dictionaries.

```python
default = bakery.get('condiment', default=True)
if 'pepper' not in def['items']:
    default['items'].append('pepper')
    default.save()
else:
    print("We already serve pepper by default")
```


**Adding a new resource**

```python
new_owl = bakery.post('cake', {
    "type": "chuck_norris",
    "name": "Round House",
    "scovilles": 16000000001  # sorry resiniferatoxin
})
```

**Fetching a subresource**

A subresource is probably what you would expect, a resource inside another
resource.  Here we get, https://a.bakery.fake/api/v1/thing/100/subthing/.

```python
thing = bakery.get('thing', 100)
subthing = thing.fetch('subthing')
```


**Non CRUD methods**

If your service has non CRUD methods, you can ask a service to "do" things
directly. Let's "BAKE /api/v1/cake/100" with some instructions in the content
body.

```python
bakery.do('bake', 'cake', 100, temp=420, time=3600)
```


Asynchronous Examples
--------

Async service connections use Tornado, http://www.tornadoweb.org/.
If this is your first time doing async programming or using tornado, you
should get familiar with it first.

Tornado Docs: http://www.tornadoweb.org/en/stable/documentation.html.

The examples below assume you are running your code from a IOLoop callback
in the same thread as the IOLoop runner.  Most of the calls made to an
async service return concurrent.Future objects so you can use all the
fun patterns available to Tornado applications.


**Creating a service connnection with Basic auth**
```python
import syndicate

bakery = syndicate.Service(uri='https://a.bakery.fake', urn='/api/v1/',
                           auth=('mrpresident', '1000xlight_points'),
                           async=True)
```


**Using Future objects directly (good)**

```python
future_result = bakery.get('cake')

def handle_response(f):
    for x in f.result():
        print("Cake is food:", x)

future_result.add_done_callback(handle_response)
```


**Using Future objects indirectly (better)**
```python
def handle_response(f):
    for x in f.result():
        print("Cake is food:", x)

bakery.get('cake', callback=handle_response)
```


**Using Future objects as yield points (best)**

NOTE: You must using the @tornado.gen.coroutine decorator from your IOLoop
callback.  A typical example is a web server URL handler that needs to fetch
foreign data.

```python
@tornado.gen.coroutine
def my_application_hook():
    cakes = yield bakery.get('cake')
    for x in cakes:
        print("Cake is food:", x)
    return cakes
```
