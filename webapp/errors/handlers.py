from flask import flash, redirect, url_for

from utils.flask_app import login


@login.unauthorized_handler
def unauthorized():
    """
    Redirect unauthorized users to Login page.
    """
    flash('You must be logged in to view that page.')
    return redirect(url_for('auth.login'))
