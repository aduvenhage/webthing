import enum

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from utils.flask_app import db, login
from utils.topic import Topic


class UserRole(enum.Enum):
    ADMINISTRATOR = 'administrator'     # can configure, read and write anything
    MANAGER = 'manager'                 # can read anything; can only write on user's own topic 
    GUEST = 'guest'                     # can only read and write on user's own topic

    @classmethod
    def default(cls):
        return cls.GUEST


class User(UserMixin, db.Model):
    """
    User details and password management.
    """

    # model attributes
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.Enum(UserRole), index=True, default=UserRole.default())

    vhost = db.Column(db.String(64), index=True, default=Topic.default_vhost())
    exchanges = db.Column(db.String(256), index=True, default=Topic.default_exchange())

    def set_password(self, password):
        # set password hash
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, role):
        return self.role == role

    def check_routing_key(self, key, permission):
        if self.has_role(UserRole.ADMINISTRATOR):
            return True

        elif self.has_role(UserRole.MANAGER) and permission == 'read':
            return True

        try:
            if (permission == 'write' or permission == 'read'):
                return self.username == Topic.get_topic_user_id(key)

        except Exception:
            pass

        # anything else fails auth
        return False

    def check_exchange(self, key, permission):
        if self.has_role(UserRole.ADMINISTRATOR):
            return True

        if (permission == 'write' or permission == 'read'):
            if self.exchanges == Topic.wildcard_exchange():
                return True

            else:
                return key in self.exchanges.split(',')

        # anything else fails auth
        return False

    def check_vhost(self, key, permission):
        if self.has_role(UserRole.ADMINISTRATOR):
            return True

        if (permission == 'write' or permission == 'read'):
            if self.vhost == Topic.wildcard_vhost():
                return True

            else:
                return key == self.vhost

        # anything else fails auth
        return False

    def __repr__(self):
        return '<User {}>'.format(self.username)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
