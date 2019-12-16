

def _topic_match(routing_key, topic, it=0, ip=0):
    """
    Recusively match the topic against routing key.
    routing_key: array: routing key words (pattern to match to)
    topic: array: topic words to match to pattern
    return: boolean
    """
    nt = len(topic)-it
    np = len(routing_key)-ip
    n = min(nt, np)

    # step through routing key pattern and topic words
    for i in range(0, n):
        sub = routing_key[i + ip]
        pub = topic[i + it]

        # match zero or more words in topic to '#' pattern word
        if sub == "#":
            if i+1 < np:
                # recursively search into topic if '#' is not last word
                for j in range(i, nt):
                    if _topic_match(routing_key=routing_key, topic=topic, it=j+it, ip=i+ip+1):
                        return True  # success

                return False  # fail

            else:
                # '#' is last pattern word
                return True  # success

        # exit if topic word does not match pattern word or wildcard
        elif pub != sub and sub != "*" and sub != "#":
            return False  # fail

    # check for trailing pattern words other than '#'
    if np > nt:
        for i in range(nt, np):
            sub = routing_key[i + ip]
            if sub != "#":
                return False  # fail

    elif nt > np:
        return False  # fail, more target words than pattern words

    return True  # success


def get_topic_match(routing_key, topic):
    """
    Match topic to routing key pattern.
    routing_key: str: routing key pattern, for example 'aa.*.cc.dd'
    topic: str: for example 'aa.bb.cc.dd'
    return: boolean
    """
    if routing_key == '#':
        return True

    elif routing_key == topic:
        return True

    else:
        routing_key_words = routing_key.split('.')
        topic_words = topic.split('.')

        return _topic_match(routing_key=routing_key_words, topic=topic_words)
