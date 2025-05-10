from db import db
from datetime import datetime
from .complete import Complete

class Plant(db.Model):
    __tablename__="plant"
    id = db.mapped_column(db.Integer, primary_key=True, autoincrement=True)
    name = db.mapped_column(db.String, nullable=False)
    schedule = db.mapped_column(db.Integer, nullable=False,  default=7)
    mood = db.mapped_column(db.Boolean, default=True)
    location = db.mapped_column(db.String, default="outdoor")
    watered = db.mapped_column(db.Boolean, default=False)
    completes = db.relationship("Complete", back_populates="plant")

    def completed(self):
        current_time = datetime.now()
        if self.watered == True:
            new_complete = Complete(date=current_time, plant=self)
            db.session.add(new_complete)
            self.watered = True
         

        

    


    


