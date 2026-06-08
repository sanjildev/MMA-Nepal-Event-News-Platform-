from app import app,db
from models import User
from werkzeug.security import generate_password_hash
from datetime import date

with app.app_context():
    admin=User(
        username='mma_admin',
        email='mmadropzone1@gmail.com',
        password=generate_password_hash('mdz123@'),
        is_admin=True,
        date_joined=str(date.today())
    )
    public=User(
        username='public',
        email='public1@gmail.com',
        password=generate_password_hash('mdz123@'),
        is_admin=False,
        date_joined=str(date.today())
    )
    db.session.add_all([admin, public])

    db.session.commit()
    print('Admin created successfully')