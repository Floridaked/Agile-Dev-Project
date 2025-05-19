from db import db
from datetime import datetime
from .complete import Complete
from sqlalchemy import desc


class Plant(db.Model):
    __tablename__="plant"
    id          = db.mapped_column(db.Integer, primary_key=True, autoincrement=True)
    name        = db.mapped_column(db.String, nullable=False)
    plant_type  = db.mapped_column(db.String, nullable=False)
    schedule    = db.mapped_column(db.Integer, nullable=False,  default=7)
    mood        = db.mapped_column(db.Boolean, default=True)
    location    = db.mapped_column(db.String, default="outdoor")
    watered     = db.mapped_column(db.Boolean, default=False)
    last_watered = db.mapped_column(db.String, default="Never")
    water_count = db.mapped_column(db.Integer, default=0)
    streak      = db.mapped_column(db.Integer, default=1)
    completes = db.relationship("Complete", back_populates="plant")
    user_id = db.mapped_column(db.Integer, db.ForeignKey("user.id"))
    owner = db.relationship("User", back_populates="plants")
    countdown = None

    def completed(self):
        current_time = datetime.now().strftime("%B %d, %Y at %I:%M%p")
        new_complete = Complete(date=current_time, plant=self)
        db.session.add(new_complete)
        self.watered = True
        self.water_count += 1

         # Increment streak if the plant is not sad
        if self.count_down() >= 0:
            self.streak += 1
        else:
            self.streak = 0  # Reset streak if the plant is sad

    def count_down(self):
        if not self.completes:
            # If the plant has never been watered, it should be watered today
            return 0

        try:
            last_watered = db.session.query(Complete).where(Complete.plant_id == self.id).order_by(desc(Complete.date)).first()
            days_since_last_watered = (datetime.now().date() - datetime.strptime(last_watered.date, "%B %d, %Y at %I:%M%p").date()).days
            count_down = self.schedule - days_since_last_watered
            return count_down
        except Exception as e:
            print(f"Error in count_down for plant {self.name}: {e}")
            return None  # Return None if an error occurs

    def was_watered_today(self):
        """Check if the plant was watered today."""
        if not self.completes:
            return False
        last_watered = db.session.query(Complete).where(Complete.plant_id == self.id).order_by(desc(Complete.date)).first()
        if last_watered:
            last_watered_date = datetime.strptime(last_watered.date, "%B %d, %Y at %I:%M%p").date()
            return last_watered_date == datetime.now().date()
        return False

        


    


