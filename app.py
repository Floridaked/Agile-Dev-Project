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
    statement = db.select(Plant).order_by(Plant.schedule.asc())
    records = db.session.execute(statement).scalars()

    return render_template("plants.html", data=records)

@app.route("/my_plants/<int:id>") 
def category_detail(id):     
    stmt = db.select(Plant).where(Plant.id == id) 
    plant = db.session.execute(stmt).scalar()
    stmt = db.select(Complete).where(Complete.plant_id == id)
    completed = db.session.execute(stmt).scalars()
    if not completed:
        completed = "No water logs"
    if not plant:
        return "Plant not found", 404
    return render_template("plant_detail.html", data=plant, complete=completed)


@app.route("/api/plants", methods=["POST"])
def add_plant():
    data = request.json
    new_plant = Plant(name=data["name"], schedule=data["schedule"])
    db.session.add(new_plant)
    db.session.commit()
    return jsonify(new_plant.to_dict())
#for adding plants need to create javascript and connect to home.html where we can have add plants form

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


@app.route("/delete/<int:id>", methods=["POST"])
def delete_plant(id):
    stmt = db.select(Plant).where(Plant.id == id)
    plant = db.session.execute(stmt).scalar()
    
    if plant:
        db.session.delete(plant)
        db.session.commit()
    
    return redirect("/my_plants")

@app.route("/watered/<int:id>", methods=["POST"])
def water_plant(id):
    stmt = db.select(Plant).where(Plant.id == id)
    plant = db.session.execute(stmt).scalar()

    if plant:
        plant.watered = True
        plant.completed()
        db.session.commit()
    return redirect("/my_plants")



if __name__ == "__main__":
    app.run(debug=True, port=8888)
