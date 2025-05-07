from db import db
import hashlib

class User(db.Model):
    __tablename__ = "user"
    id = db.mapped_column(db.Integer,primary_key=True, autoincrement=True )
    username = db.mapped_column(db.String, unique=True, nullable=False )
    password_hash = db.mapped_column(db.String, nullable=False)

    plants = db.relationship("Plant", back_populates="owner")

    def check_password(self, password):
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()

    def set_password(self, password):
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
        