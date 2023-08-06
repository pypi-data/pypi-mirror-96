from __future__ import (
    absolute_import, print_function, division, unicode_literals
)

import inspect
import ujson as json_module
import six
from six.moves import urllib

from collections import namedtuple
from collections.abc import Sequence, Sized
from functools import update_wrapper
from inflection import camelize

from zc_events.exceptions import ServiceRequestException


Call = namedtuple('Call', ['resource_type', 'params', 'response'])

_wrapper_template = """\
def wrapper%(signature)s:
    with responses:
        return func%(funcargs)s
"""


class Response(object):
    """Represents a response from an event, inspired by the requests library.

    When the client performs an action that generates a response, that response
    is represented by this class.

    Example:
    ```
    r = client.get('add', data={'x': 1, 'y': 2})
    assert r.has_errors is False
    assert r.data == 3
    assert r.errors == []

    r = client.get('add', data={'x': 1})
    assert r.has_errors is True
    assert r.data is None
    assert r.errors = .errors == [{'type': 'KeyError', 'message': "'y'"}]
    ```

    Attributes:
        data (dict, object or None): The data returned by call, if no errors occur.
        has_errors (bool): If an error was captured, it is set to True.
        errors (list of dicts): Holds the errors that were thrown, if any.
    """
    def __init__(self, response):
        for key, value in list(response.items()):
            setattr(self, key, value)


def get_wrapped(func, wrapper_template, evaldict):
    # Preserve the argspec for the wrapped function so that testing
    # tools such as pytest can continue to use their fixture injection.
    args, a, kw, defaults = inspect.getargspec(func)  # pylint: disable=deprecated-method

    signature = inspect.formatargspec(args, a, kw, defaults)  # pylint: disable=deprecated-method
    is_bound_method = hasattr(func, '__self__')
    if is_bound_method:
        args = args[1:]     # Omit 'self'
    callargs = inspect.formatargspec(args, a, kw, None)  # pylint: disable=deprecated-method

    ctx = {'signature': signature, 'funcargs': callargs}
    six.exec_(wrapper_template % ctx, evaldict)

    wrapper = evaldict['wrapper']

    update_wrapper(wrapper, func)
    if is_bound_method:
        wrapper = wrapper.__get__(func.__self__, type(func.__self__))
    return wrapper


class CallList(Sequence, Sized):

    def __init__(self):
        self._calls = []

    def __iter__(self):
        return iter(self._calls)

    def __len__(self):
        return len(self._calls)

    def __getitem__(self, idx):
        return self._calls[idx]

    def add(self, resource_type, params, response):
        self._calls.append(Call(resource_type, params, response))

    def reset(self):
        self._calls = []


class EventRequestsMock(object):
    DELETE = 'DELETE'
    GET = 'GET'
    HEAD = 'HEAD'
    OPTIONS = 'OPTIONS'
    PATCH = 'PATCH'
    POST = 'POST'
    PUT = 'PUT'

    def __init__(self, assert_all_requests_are_fired=True):
        self._calls = CallList()
        self.reset()
        self.assert_all_requests_are_fired = assert_all_requests_are_fired

    def reset(self):
        self._events = []
        self._calls.reset()

    def add(self, method, resource_type, pk=None, body='', match_querystring=False,
            query_string=None, status=200, json=None, related_resource=None):

        # if we were passed a `json` argument,
        # override the body and content_type
        if json is not None:
            body = json_module.dumps(json)

        # body must be bytes
        if isinstance(body, six.text_type):
            body = body.encode('utf-8')

        self._events.append({
            'resource_type': resource_type,
            'pk': pk,
            'method': method,
            'body': body,
            'query_string': query_string,
            'match_querystring': match_querystring,
            'status': status,
            'related_resource': related_resource,
        })

    def add_callback(self, method, url, callback, match_querystring=False,
                     content_type='text/plain'):
        self._events.append({
            'url': url,
            'method': method,
            'callback': callback,
            'content_type': content_type,
            'match_querystring': match_querystring,
        })

    @property
    def calls(self):
        return self._calls

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        success = type is None
        self.stop(allow_assert=success)
        self.reset()
        return success

    def activate(self, func):
        evaldict = {'responses': self, 'func': func}
        return get_wrapped(func, _wrapper_template, evaldict)

    def _find_match(self, resource_type, **kwargs):
        found = None
        for match in self._events:
            if kwargs['method'] != match['method']:
                continue

            if resource_type != match['resource_type']:
                continue

            if not self._has_event_match(match, **kwargs):
                continue

            found = match
            break
        else:
            return None
        if self.assert_all_requests_are_fired:
            # for each found match remove the url from the stack
            self._events.remove(found)
        return found

    def _has_event_match(self, match, **kwargs):
        pk = kwargs.get('id', None) or kwargs.get('pk', None)
        if str(match.get('pk')) != str(pk):
            return False

        if match.get('query_string') and kwargs.get('query_string') and \
                match['query_string'] != urllib.parse.unquote(kwargs['query_string']):
            return False

        if match.get('related_resource') != kwargs.get('related_resource'):
            return False

        return True

    def _on_request(self, event, **kwargs):
        resource_type = camelize(event.event_type.replace('_request', ''))

        match = self._find_match(resource_type, **kwargs)

        method = kwargs['method']

        # TODO(dcramer): find the correct class for this
        if match is None:
            error_msg = 'Service unavailable: {0} {1}'.format(method, resource_type)
            response = ServiceRequestException(error_msg)

            self._calls.add(resource_type, kwargs, response)
            raise response

        if 'body' in match and isinstance(match['body'], Exception):
            self._calls.add(resource_type, kwargs, match['body'])
            raise match['body']

        if 'body' in match:
            status = match['status']
            body = match['body']

        response = {
            'status': status,
            'body': body
        }

        self._calls.add(resource_type, kwargs, response)

        return response

    def start(self):
        try:
            from unittest import mock
        except ImportError:
            import mock

        def unbound_on_send(event, *a, **kwargs):
            return self._on_request(event, *event.args, **event.kwargs)

        self._patcher_1 = mock.patch('zc_events.client.EventClient.emit_microservice_event')

        self._patcher_2 = mock.patch('zc_events.event.ResourceRequestEvent.wait',
                                     unbound_on_send)
        self._patcher_1.start()
        self._patcher_2.start()

    def stop(self, allow_assert=True):
        self._patcher_1.stop()
        self._patcher_2.stop()
        if allow_assert and self.assert_all_requests_are_fired and self._events:
            raise AssertionError(
                'Not all requests have been executed {0!r}'.format(
                    [(url['method'], url['url']) for url in self._events]))


# expose default mock namespace
mock = _default_mock = EventRequestsMock(assert_all_requests_are_fired=False)
__all__ = []
for __attr in (a for a in dir(_default_mock) if not a.startswith('_')):
    __all__.append(__attr)
    globals()[__attr] = getattr(_default_mock, __attr)
