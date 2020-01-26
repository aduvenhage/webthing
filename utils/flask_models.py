from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from utils.flask_app import db, login
from utils.topic import get_topic_match


class User(UserMixin, db.Model):
    """
    User details and password management
    """

    # model attributes
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(64), index=True, default='guest')

    vhost = db.Column(db.String(64), index=True, default='/')
    domains = db.Column(db.String(256), index=True, default='#')
    exchanges = db.Column(db.String(256), index=True, default='#')

    def set_password(self, password):
        """
        Set new hashed password.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Check for a password match.
        """
        return check_password_hash(self.password_hash, password)

    def check_routing_key(self, key, permission):
        """
        Match a single topic string (with given permission) against all user domains.
        """
        domains = self.domains.split(',')
        if not domains:
            return False

        # NOTE: using same matching on write/pub and read/sub permissions
        if (permission == 'write' or permission == 'read'):
            for pattern in domains:
                pattern = pattern.lstrip().rstrip()
                if get_topic_match(pattern, key):
                    return True

        # anything else fails auth
        return False

    def check_exchange(self, key, permission):
        """
        Match a single exchange string (with given permission) against all user domains.
        """
        exchanges = self.exchanges.split(',')
        if not exchanges:
            return False

        # NOTE: using same matching on write and read permissions
        if (permission == 'write' or permission == 'read'):
            for pattern in exchanges:
                pattern = pattern.lstrip().rstrip()
                if get_topic_match(pattern, key):
                    return True

        # anything else fails auth
        return False

    def __repr__(self):
        return '<User {}>'.format(self.username)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
