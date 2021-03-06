from werkzeug.urls import url_parse

from flask_login import current_user, login_user, logout_user
from flask import render_template, flash, redirect, url_for, request, current_app

from utils.route_stats import route_stats
from utils.flask_models import User, UserRole

from .forms import LoginForm
from . import bp


@bp.route('/login', methods=['GET', 'POST'])
@route_stats
def login():
    """
    User login page and API.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()

    # try auth and redirect (on form POST)
    if form.validate_on_submit():
        username = form.username.data
        user = User.query.filter_by(username=username).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            current_app.logger.debug('Invalid username or password (username=%s)' % (username))

            # auth failed
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        current_app.logger.debug('Login successfull (username=%s)' % (username))

        # auth success
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')

        return redirect(next_page)

    # report form field errors
    if form.errors:
        flash(form.errors)
        current_app.logger.debug('Login failed. %s' % (str(form.errors)))

    # return login form (on GET)
    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/mq-user', methods=['POST'])
@route_stats
def mq_user():
    """
    RabbitMQ user auth
    - see https://github.com/rabbitmq/rabbitmq-auth-backend-http
    - users can have roles that affect access to management/UI (see https://www.rabbitmq.com/management.html#permissions)
    """
    def get_rabbitmq_role(user):
        # translate from UserRole to supported RabbitMQ role string
        if user.has_role(UserRole.ADMINISTRATOR):
            return 'administrator'
        elif user.has_role(UserRole.MANAGER):
            return 'management'
        else:
            return 'guest'

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

    if user.role:
        current_app.logger.debug('MQ user allowed (username=%s, role=%s)' % (username, user.role))
        return "allow " + get_rabbitmq_role(user)

    else:
        current_app.logger.debug('MQ user allowed (username=%s)' % (username))
        return "allow"


@bp.route('/mq-vhost', methods=['POST'])
@route_stats
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
    if not user.check_vhost(vhost, 'write'):
        current_app.logger.debug('MQ user/vhost denied (username=%s, vhost=%s)' % (username, vhost))
        return "deny"

    current_app.logger.debug('MQ user/vhost allowed (username=%s, vhost=%s)' % (username, vhost))
    return "allow"


@bp.route('/mq-resource', methods=['POST'])
@route_stats
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
    if not user.check_vhost(vhost, 'write'):
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
@route_stats
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
    if not user.check_vhost(vhost, 'write'):
        current_app.logger.debug('MQ user/vhost denied (username=%s, vhost=%s)'
                                 % (username, vhost))
        return "deny"

    # check user routing keys
    routing_key = request.form.get('routing_key', '')
    permission = request.form.get('permission', '')

    if not user.check_routing_key(routing_key, permission):
        current_app.logger.debug('MQ user/topic denied (username=%s, routing_key=%s, permission=%s)'
                                 % (username, routing_key, permission))
        return "deny"

    # check user access to specific exchanges
    resource_type = request.form.get('resource', '')
    resource_name = request.form.get('name', '')

    if resource_type == 'topic':
        if not user.check_exchange(resource_name, permission):
            current_app.logger.debug('MQ user/exchange denied (username=%s, exchange=%s, permission=%s)'
                                     % (username, resource_name, permission))
            return "deny"

    current_app.logger.debug('MQ user/topic allowed (username=%s, vhost=%s, resource=%s, name=%s, routing_key=%s, permission=%s)'
                             % (username, vhost, resource_type, resource_name, routing_key, permission))

    return "allow"
