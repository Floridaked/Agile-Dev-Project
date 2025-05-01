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



@app.route("/add_plant", methods=["GET", "POST"])
def add_plant_page():
    if request.method == "POST":
        name = request.form["name"]
        schedule = int(request.form["schedule"])
        new_plant = Plant(name=name, schedule=schedule)
        db.session.add(new_plant)
        db.session.commit()
        return redirect("/my_plants")
    return render_template("add_plant.html")

@app.route("/edit_plant/<int:id>", methods=["GET", "POST"])
def edit_plant(id):
    plant = db.session.get(Plant, id)
    if not plant:
        return "Plant not found", 404

    if request.method == "POST":
        plant.name = request.form["name"]
        plant.schedule = int(request.form["schedule"])
        db.session.commit()
        return redirect("/my_plants")

    return render_template("edit_plant.html", plant=plant)

if __name__ == "__main__":
    app.run(debug=True, port=8888)
