from db import db
from flask import *
from models import *
from app import app
import csv

def drop_tables():
    db.drop_all()

def create_tables():
    db.create_all()
    new_user = User(username="admin")
    new_user.set_password("123")
    db.session.add(new_user)
    db.session.commit()

if __name__ =="__main__":

    with app.app_context():
        drop_tables()
        create_tables()
        