# -*- coding: utf-8 -*-

import sys
import logging

from fast_tracker.common.object_names import callable_name
from fast_tracker.common.object_wrapper import (wrap_function_wrapper,
                                                function_wrapper)
from fast_tracker.api.transaction import current_transaction
from fast_tracker.api.time_trace import record_exception
from fast_tracker.api.wsgi_application import wrap_wsgi_application
from fast_tracker.core.config import ignore_status_code
from fast_tracker.api.function_trace import function_trace

_logger = logging.getLogger(__name__)


def _bind_handle_exception_v1(ex, req, resp, *args, **kwargs):
    return resp


def _bind_handle_exception_v2(req, resp, *args, **kwargs):
    return resp


def build_wrap_handle_exception(bind_handle_exception):
    def wrap_handle_exception(wrapped, instance, args, kwargs):
        transaction = current_transaction()

        if transaction is None:
            return wrapped(*args, **kwargs)

        name = callable_name(wrapped)
        transaction.set_transaction_name(name, priority=1)

        result = wrapped(*args, **kwargs)
        if result:
            exc_info = sys.exc_info()
            try:
                resp = bind_handle_exception(*args, **kwargs)
                response_code = int(resp.status.split()[0])
                if ignore_status_code(response_code):
                    return result
                record_exception(*exc_info)
            except:
                record_exception(*exc_info)
            finally:
                exc_info = None

        return result

    return wrap_handle_exception


@function_wrapper
def method_wrapper(wrapped, instance, args, kwargs):
    transaction = current_transaction()

    if transaction is None:
        return wrapped(*args, **kwargs)

    name = callable_name(wrapped)
    transaction.set_transaction_name(name, priority=2)

    traced_method = function_trace(name=name)(wrapped)
    return traced_method(*args, **kwargs)


def wrap_responder(wrapped, instance, args, kwargs):
    method_map = wrapped(*args, **kwargs)
    for key, method in method_map.items():
        method_map[key] = method_wrapper(method)

    return method_map


def framework_details():
    import falcon
    return 'Falcon', getattr(falcon, '__version__', None)


def instrument_falcon_api(module):
    framework = framework_details()

    version = framework[1].split('.')
    if version[0] < '1' or framework[1] == '1.0.0':
        wrap_handle_exception = \
            build_wrap_handle_exception(_bind_handle_exception_v1)
        _logger.warning('falcon <= 1.0.0时,API对象没有_handle_exception方法,虽然这不影响数据的采集,但还是建议升级falcon')

    elif version[0] < '2':
        wrap_handle_exception = \
            build_wrap_handle_exception(_bind_handle_exception_v1)
        wrap_function_wrapper(module, 'API._handle_exception',
                              wrap_handle_exception)

    else:
        wrap_handle_exception = \
            build_wrap_handle_exception(_bind_handle_exception_v2)
        wrap_function_wrapper(module, 'API._handle_exception',
                              wrap_handle_exception)

    wrap_wsgi_application(module, 'API.__call__',
                          framework=framework)


def instrument_falcon_app(module):
    framework = framework_details()
    version = framework[1].split('.')

    wrap_handle_exception = \
        build_wrap_handle_exception(_bind_handle_exception_v2)

    wrap_wsgi_application(module, 'App.__call__',
                          framework=framework)
    if version[0] < '1' or framework[1] == '1.0.0':
        _logger.warning('falcon <= 1.0.0时,API对象没有_handle_exception方法,虽然这不影响数据的采集,但还是建议升级falcon')
        return
    wrap_function_wrapper(module, 'App._handle_exception',
                          wrap_handle_exception)


def instrument_falcon_routing_util(module):
    if hasattr(module, 'map_http_methods'):
        wrap_function_wrapper(module, 'map_http_methods',
                              wrap_responder)
    elif hasattr(module, 'create_http_method_map'):
        wrap_function_wrapper(module, 'create_http_method_map',
                              wrap_responder)
