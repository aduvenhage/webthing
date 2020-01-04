

def _topic_match(pattern, topic, it=0, ip=0):
    """
    Recusively match the topic against routing key.
    routing_key: array: routing key words (pattern to match to)
    topic: array: topic words to match to pattern

    return: boolean
    """
    nt = len(topic)-it
    np = len(pattern)-ip
    n = min(nt, np)

    # step through routing key pattern and topic words
    for i in range(0, n):
        sub = pattern[i + ip]
        pub = topic[i + it]

        # match zero or more words in topic to '#' pattern word
        if sub == '#':
            if i+1 < np:
                # recursively search into topic if '#' is not last word
                for j in range(i, nt):
                    if _topic_match(pattern=pattern, topic=topic, it=j+it, ip=i+ip+1):
                        return True  # success

                return False  # fail

            else:
                # '#' is last pattern word
                return True  # success

        # exit if pattern word does not match topic word or wildcard
        elif pub != sub and sub != '*' and sub != '#':
            return False  # fail

    # check for trailing pattern words other than '#'
    if np > nt:
        for i in range(nt, np):
            sub = pattern[i + ip]
            if sub != '#':
                return False  # fail

    elif nt > np:
        return False  # fail, more target words than pattern words

    return True  # success


def get_topic_match(pattern, topic):
    """
    Match topic to pattern.
    pattern: str: subscription pattern, for example 'aa.*.cc.dd'
    topic: str: for example 'aa.bb.cc.dd'

    return: boolean
    """
    if pattern == '#':
        return True

    elif pattern == topic:
        return True

    else:
        pattern_words = pattern.split('.')
        topic_words = topic.split('.')

        return _topic_match(pattern=pattern_words, topic=topic_words)
