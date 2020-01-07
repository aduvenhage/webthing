from . import bp

from flask_login import current_user, login_user, logout_user
from flask import render_template, flash, redirect, url_for, request, current_app

from utils.view_stats import view_stats

from .models import User
from .forms import LoginForm


@bp.route('/login', methods=['GET', 'POST'])
@view_stats
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            current_app.logger.debug('Invalid username or password (username=%s)' % (username))

            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        current_app.logger.debug('Login successfull (username=%s)' % (username))

        return redirect(url_for('main.index'))

    if form.errors:
        flash(form.errors)
        current_app.logger.debug('Login failed. %s' % (str(form.errors)))

    return render_template('login.html', title='Sign In', form=form)


@bp.route('/mq-user', methods=['POST'])
@view_stats
def mq_user():
    """
    RabbitMQ user auth
    (see https://github.com/rabbitmq/rabbitmq-auth-backend-http)
    """
    username = request.form.get('username', '')
    user = User.query.filter_by(username=username).first()

    # authenticate user
    if user is None:
        current_app.logger.debug('MQ user denied (username=%s)' % (username))
        return "deny"

    password = request.form.get('password', '')
    if not user.check_password(password):
        current_app.logger.debug('MQ user denied (username=%s)' % (username))
        return "deny"

    # NOTE: users can have one of many roles that affect access (see https://www.rabbitmq.com/management.html#permissions) to management/UI
    if user.role:
        current_app.logger.debug('MQ user allowed (username=%s, role=%s)' % (username, user.role))
        return "allow " + str(user.role)

    else:
        current_app.logger.debug('MQ user allowed (username=%s)' % (username))
        return "allow"



@bp.route('/mq-vhost', methods=['POST'])
@view_stats
def mq_vhost():
    """
    RabbitMQ vhost access
    (see https://github.com/rabbitmq/rabbitmq-auth-backend-http)
    """
    username = request.form.get('username', '')
    user = User.query.filter_by(username=username).first()

    if user is None:
        current_app.logger.debug('MQ user denied (username=%s)' % (username))
        return "deny"

    # check for user access to this virtual host
    vhost = request.form.get('vhost', '')
    if user.vhost != vhost:
        current_app.logger.debug('MQ user/vhost denied (username=%s, vhost=%s)' % (username, vhost))
        return "deny"

    current_app.logger.debug('MQ user/vhost allowed (username=%s, vhost=%s)' % (username, vhost))
    return "allow"


@bp.route('/mq-resource', methods=['POST'])
@view_stats
def mq_resource():
    """
    RabbitMQ resource access
    (see https://github.com/rabbitmq/rabbitmq-auth-backend-http)
    """
    username = request.form.get('username', '')
    user = User.query.filter_by(username=username).first()

    if user is None:
        current_app.logger.debug('MQ user denied (username=%s)' % (username))
        return "deny"

    # check for user access to this virtual host
    vhost = request.form.get('vhost', '')
    if user.vhost != vhost:
        current_app.logger.debug('MQ user/vhost denied (username=%s, vhost=%s)' % (username, vhost))
        return "deny"

    # check user access to specific exchanges
    resource_type = request.form.get('resource', '')
    resource_name = request.form.get('name', '')
    permission = request.form.get('permission', '')

    if resource_type == 'exchange':
        if not user.check_exchange(resource_name, permission):
            current_app.logger.debug('MQ user/exchange denied (username=%s, exchange=%s, permission=%s)'
                                     % (username, resource_name, permission))
            return "deny"

    current_app.logger.debug('MQ user/resource allowed (username=%s, vhost=%s, resource=%s, name=%s, permission=%s)'
                             % (username, vhost, resource_type, resource_name, permission))

    return "allow"


@bp.route('/mq-topic', methods=['POST'])
@view_stats
def mq_topic():
    """
    RabbitMQ topic access
    (see https://github.com/rabbitmq/rabbitmq-auth-backend-http)
    """
    username = request.form.get('username', '')
    user = User.query.filter_by(username=username).first()

    if user is None:
        current_app.logger.debug('MQ user denied (username=%s)' % (username))
        return "deny"

    # check for user access to this virtual host
    vhost = request.form.get('vhost', '')
    if user.vhost != vhost:
        current_app.logger.debug('MQ user/vhost denied (username=%s, vhost=%s)'
                                 % (username, vhost))
        return "deny"

    # NOTE: try to match auth topic key to user routing keys
    routing_key = request.form.get('routing_key', '')
    permission = request.form.get('permission', '')

    if not user.check_routing_key(routing_key, permission):
        current_app.logger.debug('MQ user/topic denied (username=%s, routing_key=%s, permission=%s)'
                                 % (username, routing_key, permission))
        return "deny"

    # check user access to specific exchanges
    topic_resource = request.form.get('resource', '')  # should always be 'topic'
    exchange_name = request.form.get('name', '')
    permission = request.form.get('permission', '')

    if not user.check_exchange(exchange_name, permission):
        current_app.logger.debug('MQ user/exchange denied (username=%s, exchange=%s, permission=%s)'
                                 % (username, exchange_name, permission))
        return "deny"

    current_app.logger.debug('MQ user/topic allowed (username=%s, vhost=%s, resource=%s, name=%s, routing_key=%s, permission=%s)'
                             % (username, vhost, topic_resource, exchange_name, routing_key, permission))

    return "allow"
