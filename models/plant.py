from db import db

class Plant(db.Model):
    __tablename__="plant"
    id = db.mapped_column(db.Integer, primary_key=True, autoincrement=True)
    name = db.mapped_column(db.String, nullable=False)
    schedule = db.mapped_column(db.Integer, nullable=False,  default=7)
    mood = db.mapped_column(db.Boolean, default=True)
    


    


