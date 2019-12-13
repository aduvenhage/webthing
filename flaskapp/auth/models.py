
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from flaskapp import db, login
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
    routing_keys = db.Column(db.String(256), index=True, default='#')

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

    def check_topics(self, topic):
        """
        Match a single topic string against any user routing keys
        """
        keys = self.routing_keys.split(',')
        if not keys:
            return False

        for key in keys:
            if get_topic_match(key, topic):
                return True

        return False

    def __repr__(self):
        return '<User {}>'.format(self.username)


@login.user_loader
def load_user(id):
    """
    Utility function (used by flask_login) that helps load user object for session.
    """
    return User.query.get(int(id))
