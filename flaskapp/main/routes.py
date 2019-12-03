from . import bp


from werkzeug.exceptions import HTTPException
from flask import request, abort

from utils.view_stats import view_stats


@bp.route('/')
@bp.route('/index')
def index():
    return "Hello, World!"
