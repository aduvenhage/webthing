import logging
from functools import wraps

from werkzeug.exceptions import HTTPException
from flask import request

from utils.stats import stats


logger = logging.getLogger(__file__)


def view_incr_stats(route_name, method, status_code=None):
    """
    Increments relevant stats counters.
    """
    if status_code:
        stats().incr("responses.status.{}.{}.status.{}".format(route_name, method, status_code))

    stats().incr("responses.{}".format(route_name))
    stats().incr("responses.{}.{}".format(route_name, method))


def view_stats(func):
    """
    Decorator that ads request/response stats counters to view methods.
    """
    @wraps(func)
    def _wrapped(*args, **kwargs):
        route_name = request.path if request.path else 'unknown_route'
        method = request.method

        try:
            with stats().timer('timer.{}'.format(route_name)):
                # Call the view -- assumes view method returns (response, status_code)
                response = func(*args, **kwargs)

            view_incr_stats(route_name, method,
                            response[1] if len(response) > 1 else None)

            return response

        except HTTPException as e:
            view_incr_stats(route_name, method, e.code)
            raise

        except Exception as e:
            # assume internal server error
            view_incr_stats(route_name, method, 500)
            raise

    return _wrapped
