import os
import click

from flaskapp.auth.models import User
from flaskapp import create_app
from flaskapp import db


@click.command()
@click.option('--erase_all', is_flag=True, required=False, help='Erase all users profiles.')
@click.option('--file', default=None, type=str, help='User backup file (JSON).')
def main(erase_all, file):
    # init flask app
    app = create_app()
    app.app_context().push()

    # clean out DB
    if erase_all:
        User.query.delete()
        db.session.commit()

    # create default super user
    print('Creating superuser object ...')
    u = User(username='admin',
             email='aduvenhage@gmail.com',
             role='administrator',
             routing_keys='#')

    passw = os.getenv('APP_PASSWORD', 'admin')
    u.set_password(passw)

    # update db
    print('Updating to DB ...')
    db.session.add(u)
    db.session.commit()

    print('Success.')


if __name__ == '__main__':
    main()
