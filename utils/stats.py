import statsd


__stats_client = None


def stats(config=None):
    global __stats_client

    if not __stats_client:
        __stats_client = statsd.StatsClient(config.STATS_HOST, config.STATS_PORT)

    return __stats_client
