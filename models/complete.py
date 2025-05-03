from db import db

class Complete(db.Model):
    __tablename__="complete"
    id = db.mapped_column(db.Integer, primary_key=True, autoincrement=True)
    date = db.mapped_column(db.String, nullable=False)
    plant_id = db.mapped_column(db.Integer, db.ForeignKey('plant.id'))
    plant = db.relationship("Plant", back_populates="completes")
    