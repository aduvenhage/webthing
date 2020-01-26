import logging
from functools import wraps

from werkzeug.exceptions import HTTPException
from flask import request, make_response

from utils.stats import stats


logger = logging.getLogger(__file__)


def _incr_stats(route_name, method, status_code=None):
    """
    Increments relevant stats counters.
    """
    if status_code:
        stats().incr("responses.status.{}.{}.status.{}".format(route_name, method, status_code))

    stats().incr("responses.{}".format(route_name))
    stats().incr("responses.{}.{}".format(route_name, method))


def route_stats(func):
    """
    Decorator that ads request/response stats counters to view methods.
    """
    @wraps(func)
    def _wrapped(*args, **kwargs):
        route_name = request.path if request.path else 'unknown_route'
        method = request.method

        try:
            with stats().timer('timer.{}'.format(route_name)):
                response = func(*args, **kwargs)
                response = make_response(response)

            _incr_stats(route_name, method, response.status_code)

            return response

        except HTTPException as e:
            _incr_stats(route_name, method, e.code)
            raise

        except Exception:
            # assume internal server error
            _incr_stats(route_name, method, 500)
            raise

    return _wrapped
