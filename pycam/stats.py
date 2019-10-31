import statsd



# default config
__stats_config = {
    'host': 'localhost',
    'port': 8125
}

__stats_client = None


def stats_config():
    return __stats_config


def stats():
    global __stats_client

    if not __stats_client:
        __stats_client = statsd.StatsClient(stats_config()['host'],
                                            stats_config()['port'])

    return __stats_client
