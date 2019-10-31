import statsd
from config import stats_config


__stats_client = None


def stats():
    global __stats_client

    if not __stats_client:
        __stats_client = statsd.StatsClient(stats_config()['host'],
                                            stats_config()['port'])

    return __stats_client
