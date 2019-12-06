
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from flaskapp import db, login


class User(UserMixin, db.Model):
    """
    User details and password management
    """

    # model attributes 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

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

    def __repr__(self):
        return '<User {}>'.format(self.username)


@login.user_loader
def load_user(id):
    """
    Utility function (used by flask_login) that helps load user object for session.
    """
    return User.query.get(int(id))
