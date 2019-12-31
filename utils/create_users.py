import os
import click
import json

from flaskapp.auth.models import User
from flaskapp import create_app
from flaskapp import db

from config import config


@click.command()
@click.option('--erase_all', is_flag=True, required=False, help='Erase all users profiles.')
@click.option('--file', default=None, type=str, help='User backup file (JSON).')
def main(erase_all, file):
    """
    Create (and optionally erase) required user profiles.
    See click options above.

    NOTES:
    - to create a new DB, see 'deployment/server/create_db.sh'

    User file format (JSON):

        [
            {
                "username": "user1",
                "password": "passw1",
                "role": "administrator",
                "routing_keys": "user1.#"
            },

            ...

        ]

    """

    # init flask app
    # NOTE: will also load config
    config = config()
    config.AMQP_USERNAME = config.get('AMQP_USERNAME', 'guest')
    config.AMQP_PASSWORD = config.get('AMQP_PASSWORD', 'guest')

    app = create_app()
    app.app_context().push()

    # optionally clean out DB
    if erase_all:
        User.query.delete()
        db.session.commit()

    # create default super user
    print('Creating superuser object ...')
    u = User(username=config.AMQP_USERNAME,
             email='aduvenhage@gmail.com',
             role='administrator',
             routing_keys='#')

    passw = config.AMQP_PASSWORD
    u.set_password(passw)

    db.session.add(u)
    db.session.commit()

    # create additional users from user backup file
    if file:
        with open(file, 'r') as f:
            datastore = json.load(f)

            for user in datastore:
                passw = user.pop('password')

                u = User(**user)
                u.set_password(passw)

                db.session.add(u)
                db.session.commit()

    print('Success.')


if __name__ == '__main__':
    main()
