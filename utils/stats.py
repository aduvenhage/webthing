import statsd

from utils.config import config


__stats_client = None


def stats():
    global __stats_client

    if not __stats_client:
        cfg = config()
        cfg.get('STATS_HOST', 'localhost')
        cfg.get('STATS_PORT', 8125)

        __stats_client = statsd.StatsClient(cfg.STATS_HOST, cfg.STATS_PORT)

    return __stats_client
