import os

from flaskapp.auth.models import User
from flaskapp import create_app
from flaskapp import db



def main():
    # init flask app
    app = create_app()
    app.app_context().push()

    # create user
    u = User(username='Arno', 
             email='a.rno')
    u.set_password('123456')

    # update db
    db.session.add(u)
    db.session.commit()



if __name__ == '__main__':
    main()
