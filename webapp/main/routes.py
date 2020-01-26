from flask_login import login_required

from utils.route_stats import route_stats

from . import bp


@bp.route('/')
@bp.route('/index')
@route_stats
@login_required
def index():
    return "Hello, World!"
