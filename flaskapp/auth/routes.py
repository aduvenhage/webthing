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

    username = request.form.get('username', '')
    user = User.query.filter_by(username=username).first()

    if user:
        password = request.form.get('password', '')

        if user.check_password(password):
            if user.role:
                current_app.logger.debug('MQ user allowed (username=%s, role=%s)' % (username, user.role))
                return "allow " + str(user.role)

            else:
                current_app.logger.debug('MQ user allowed (username=%s)' % (username))
                return "allow"

    current_app.logger.debug('MQ user denied (username=%s)' % (username))

    return "deny"


@bp.route('/mq-vhost', methods=['POST'])
@view_stats
def mq_vhost():
    username = request.form.get('username', '')
    user = User.query.filter_by(username=username).first()

    if user:
        vhost = request.form.get('vhost', '')
        if user.vhost == vhost:
            current_app.logger.debug('MQ user/vhost allowed (username=%s, vhost=%s)' % (username, vhost))
            return "allow"

        else:
            current_app.logger.debug('MQ user/vhost denied (username=%s, vhost=%s)' % (username, vhost))
            return "deny"

    return "deny"


@bp.route('/mq-resource', methods=['POST'])
@view_stats
def mq_resource():
    username = request.form.get('username', '')
    user = User.query.filter_by(username=username).first()

    if user:
        vhost = request.form.get('vhost', '')
        resource = request.form.get('resource', '')
        name = request.form.get('name', '')
        permission = request.form.get('permission', '')

        current_app.logger.debug('MQ user/resource allowed (username=%s, vhost=%s, resource=%s, name=%s)' 
                                 % (username, vhost, resource, name))

        return "allow"

    return "deny"


@bp.route('/mq-topic', methods=['POST'])
@view_stats
def mq_topic():
    username = request.form.get('username', '')
    user = User.query.filter_by(username=username).first()

    if user:
        vhost = request.form.get('vhost', '')
        resource = request.form.get('resource', '')
        name = request.form.get('name', '')
        permission = request.form.get('permission', '')
        routing_key = request.form.get('routing_key', '')

        current_app.logger.debug('MQ user/topic allowed (username=%s, vhost=%s, resource=%s, name=%s, routing_key=%s)' 
                                 % (username, vhost, resource, name, routing_key))

        return "allow"

    return "allow"
