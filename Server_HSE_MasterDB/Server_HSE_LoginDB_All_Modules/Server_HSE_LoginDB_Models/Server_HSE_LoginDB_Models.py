from flask import Flask
from flask_login import UserMixin
from Server_HSE_MasterDB import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    def __repr__(self):
        return f"User('{self.id}','{self.username}','{self.email}','{self.password}')"