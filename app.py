from flask import *
from pathlib import Path
from db import db
from models import *
from datetime import datetime as dt
from pathlib import Path






app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.instance_path = Path(".").resolve()

db.init_app(app)


@app.route("/") 
def home(): 
    return render_template("home.html")


@app.route("/my_plants") 
def categories(): 
    statement = db.select(Plant)
    records = db.session.execute(statement).scalars()
    return render_template("plants.html", data=records)

@app.route("/my_plants/<string:name>") 
def category_detail(name):     
    stmt = db.select(Plant).where(Plant.name == name) 
    plant = db.session.execute(stmt).scalar()
    return render_template("plant_detail.html", data=plant)

@app.route("/api/plants", methods=["POST"])
def add_plant():
    data = request.json
    new_plant = Plant(name=data["name"], schedule=data["schedule"])
    db.session.add(new_plant)
    db.session.commit()
    return jsonify(new_plant.to_dict())
#for adding plants need to create javascript and connect to home.html where we can have add plants form


if __name__ == "__main__":
    app.run(debug=True, port=8888)
