syndicate
===========
_*A wrapper for REST APIs*_

[![Maturity](https://img.shields.io/pypi/status/syndicate.svg)](https://pypi.python.org/pypi/syndicate)
[![License](https://img.shields.io/pypi/l/syndicate.svg)](https://pypi.python.org/pypi/syndicate)
[![Change Log](https://img.shields.io/badge/change-log-blue.svg)](https://github.com/mayfield/syndicate/blob/master/CHANGELOG.md)
[![Build Status](https://semaphoreci.com/api/v1/projects/50fbd264-8014-4fbd-9295-c99c65c8b05a/533670/shields_badge.svg)](https://semaphoreci.com/mayfield/syndicate)
[![Version](https://img.shields.io/pypi/v/syndicate.svg)](https://pypi.python.org/pypi/syndicate)


About
--------

Syndicate is a library for using HTTP based REST APIs.  This provides a means
to generically handle serialization (JSON, XML) and URI mapping as seen in many
of the REST APIs published these days.  Currently Tastypie APIs are the primary
target but the system should be compossible enough to work with other APIs if they
work roughly the same way.


Requirements
--------

* Requests (sync mode)
* aiohttp (async mode)


Installation
--------

    python ./setup.py build
    python ./setup.py install


Compatibility
--------

* Python 3.4+


TODO
--------

* Unified authentication between HTTP adapters.
* Documentation


Getting Started
--------

Syndicate has two basic modes for communicating with an API, sync and async.
The sync mode uses the 'requests' library as the HTTP adapter and the async
mode uses `aiohttp`.  An adapter can be provided by the user if they have
their own backend.

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


**Adding a new resource**

```python
new_owl = bakery.post('cake', {
    "type": "chuck_norris",
    "name": "Round House",
    "scovilles": 16000000001  # sorry resiniferatoxin
})
```

**Non CRUD methods**

If your service has non CRUD methods, you can ask a service to "do" things
directly. Let's "BAKE /api/v1/cake/100" with some instructions in the content
body.

```python
bakery.do('bake', 'cake', 100, temp=420, time=3600)
```
