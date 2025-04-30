from db import db
from flask import *
from models import *
from app import app
import csv

def drop_tables():
    db.drop_all()

def create_tables():
    db.create_all()

# made the csv just to test        
def import_customers_from_csv():
    with open("plant.csv", encoding="utf-8") as fp:
        reader = csv.reader(fp)
      
        for row in reader:
            customer = Plant(name=row[0], schedule=row[1], mood=row[2].strip() == 'True')
            db.session.add(customer)
        db.session.commit()


if __name__ =="__main__":

    with app.app_context():
        drop_tables()
        create_tables()
        import_customers_from_csv()
        