from . import create_app, db
from .models import User
import getpass

def create_admin():
    app = create_app()
    with app.app_context():
        db.create_all()
        
        print(f"Using database: {app.config['SQLALCHEMY_DATABASE_URI']}")

        username = input("Enter admin username: ")
        if User.query.filter_by(username=username).first():
            print(f"User '{username}' already exists.")
            return

        password = getpass.getpass("Enter admin password: ")

        user = User(username=username)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        print(f"Admin user '{username}' created successfully.")

if __name__ == '__main__':
    create_admin()