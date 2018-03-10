from server import db
from passlib.hash import argon2


class User(db.Model):
     
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    verified = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(self, email, password, first_name, last_name):
        self.email = email
        self.password = argon2.hash(password)
        self.first_name = first_name
        self.last_name = last_name

    def authenticate(self, password):
        return argon2.verify(password, self.password)

    def change_password(self, old_password, new_password):
        if not argon2.verify(old_password, self.password):
            return False
        self.password = argon2.hash(new_password)
        self.save()
        return True
