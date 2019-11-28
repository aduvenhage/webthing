from . import bp


@bp.route('/mq-user', methods=['POST'])
def mq_user():
    return "allow administrator"


@bp.route('/mq-vhost', methods=['POST'])
def mq_vhost():
    return "allow"


@bp.route('/mq-resource', methods=['POST'])
def mq_resource():
    return "allow"


@bp.route('/mq-topic', methods=['POST'])
def mq_topic():
    return "allow"
