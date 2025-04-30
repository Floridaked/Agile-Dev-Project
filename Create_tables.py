from db import db
from flask import *
from models import *
from app import app
import csv

def drop_tables():
    db.drop_all()

def create_tables():
    db.create_all()

if __name__ =="__main__":

    with app.app_context():
        drop_tables()
        create_tables()
        