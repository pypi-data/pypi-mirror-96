# RESTClient
The cross-platform tool to work with http.


## Installation
For most users, the recommended method to install is via pip:
```cmd
pip install pyrestclient
```

or from source:

```cmd
python setup.py install
```

## Import

```python
from pyrestclient import RESTClient
```

---

## Changelog

##### 1.0.6 (24.02.2021)

- refactoring. used lazy initialization to get token
- wait_service_start: for the is_service_initialized under the hood used 0.1 sec by default

##### 1.0.5 (24.02.2021)

is_service_initialized updated to use timeout

##### 1.0.4 (21.12.2020)

logger auth link fixed

##### 1.0.3 (21.12.2020)

header param added to the GET method

##### 1.0.2 (31.10.2020)

New base method added:

- is_host_available (Check remote host availability using socket and specified port)
- is_service_initialized (GET https://{IP}:{PORT})
- wait_service_start

##### 1.0.1 (29.10.2020)

- PUT fixed
- RESTClient inherited from RESTAssertion. No need to import RESTAssertion directly

#####1.0.0 (14.10.2020)
- removed "extend_header"


#####0.1.0 (21.05.2020)
- file logging removed

#####0.0.9 (28.03.2020)
DELETE fixed
POST: added file support

#####0.0.8 (28.03.2020)
header typing hint fixed. Now it is dict

#####0.0.7 (10.03.2020)
- Added query_params to all methods
- POST method was refactored to use .send_request()


#####0.0.6 (01.03.2020)
- removed full_url param. now it will automatically convert url. use "http[s]://site.com" format in methods to use full url.
- code refactoring

#####0.0.5 (01.03.2020)
- query params refactored to use urlencode
- added DELETE method

##### 0.0.4 (27.02.2020)
should_be_bad_request: assert text fixed
...

##### 0.0.1 (9.02.2020)
- initial commit