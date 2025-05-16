from db import db
import hashlib
from datetime import datetime as dt


class Achievement(db.Model):
    __tablename__ = "achievement"
    id = db.mapped_column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.mapped_column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    medal = db.mapped_column(db.String, nullable=False)  # Medal type (Gold, Silver, Bronze)
    date_earned = db.mapped_column(db.DateTime, default=dt.utcnow)  # Date the medal was earned

    user = db.relationship("User", back_populates="achievements")


class User(db.Model):
    __tablename__ = "user"
    id = db.mapped_column(db.Integer, primary_key=True, autoincrement=True)
    username = db.mapped_column(db.String, unique=True, nullable=False)
    password_hash = db.mapped_column(db.String, nullable=False)
    water_streak = db.mapped_column(db.Integer, default=0)
    plant_streak = db.mapped_column(db.Integer, default=0)
    day_streak = db.mapped_column(db.Integer, default=0)  # New field for day streak
    last_active_date = db.mapped_column(db.Date, nullable=True)  # New field for last active date


    # Define the relationship with Achievement
    achievements = db.relationship("Achievement", back_populates="user", cascade="all, delete-orphan")

    plants = db.relationship("Plant", back_populates="owner")

    def check_password(self, password):
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()

    def set_password(self, password):
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()