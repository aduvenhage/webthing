import statsd

from utils.config import get_config


__stats_client = None


def stats():
    global __stats_client

    if not __stats_client:
        config = get_config()
        config.get('STATS_HOST', 'localhost')
        config.get('STATS_PORT', 8125)

        __stats_client = statsd.StatsClient(config.STATS_HOST, config.STATS_PORT)

    return __stats_client
