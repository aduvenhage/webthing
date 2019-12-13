import os
import re

from flaskapp.auth.models import User
from flaskapp import create_app
from flaskapp import db


def main():
    # init flask app
    app = create_app()
    app.app_context().push()

    # create user
    print('Creating superuser object ...')
    u = User(username='admin',
             email='aduvenhage@gmail.com',
             role='administrator',
             routing_keys='admin.#,#.jpeg')

    passw = os.getenv('APP_PASSWORD', 'admin')
    u.set_password(passw)

    res = u.check_topics('admin2.cam1.jpeg')
    res = u.check_topics('admin.cam2')
    res = u.check_topics('admi.cam')

    # update db
    print('Updating to DB ...')
    db.session.add(u)
    db.session.commit()

    print('Success.')


if __name__ == '__main__':
    main()
