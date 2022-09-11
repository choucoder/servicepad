from datetime import datetime

from werkzeug.security import generate_password_hash

from database.connection import db


class User(db.Model): 
    id = db.Column(db.Integer, primary_key = True)
    fullname = db.Column(db.String(128))
    email = db.Column(db.String(), unique=True, nullable=False)
    photo = db.Column(db.String(), nullable=True)
    password = db.Column(db.String())
 
    def __init__(self, fullname, email, password):
        self.fullname = fullname
        self.email = email
        self.password = password

    def __repr__(self):
        return f"{self.fullname}:{self.email}"

    def update(self, data):
        for name, value in data.items():
            if name == 'password':
                setattr(self, name, generate_password_hash(value))
            else:
                setattr(self, name, value)
        db.session.add(self)
        db.session.commit()