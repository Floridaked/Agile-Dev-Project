from flask import *
from pathlib import Path
from db import db
from models import *
from datetime import datetime as dt
from pathlib import Path
import requests as http_requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
# Ensure the .env file is in the same directory as this script
# or provide the full path to the .env file
load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.instance_path = Path(".").resolve()

db.init_app(app)
app.secret_key = 'secret-key????'

@app.route("/") 
def home(): 
    return render_template("home.html")

@app.route("/my_plants") 
def plants(): 
   
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    statement = db.select(Plant).where(Plant.user_id == user_id).order_by(Plant.schedule.asc())
    records = db.session.execute(statement).scalars().all()      # .all() to allow looping
    statement = db.select(User).where(User.id == user_id)
    user = db.session.execute(statement).scalar()

    return render_template("plants.html", data=records, user=user)

@app.route("/my_plants/<int:id>") 
def plant_detail(id):   
    stmt        = db.select(Plant).where(Plant.id == id) 
    plant       = db.session.execute(stmt).scalar()
    stmt        = db.select(Complete).where(Complete.plant_id == id)
    completed   = list(db.session.execute(stmt).scalars())
    if not plant:
        return "Plant not found", 404
    return render_template("plant_detail.html", data=plant, complete=completed)


@app.route("/api/plants", methods=["POST"])
def add_plant():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    name = request.form.get("name")
    schedule = request.form.get("schedule")

    new_plant = Plant(name=name, schedule=int(schedule), user_id=session['user_id'])
    db.session.add(new_plant)
    db.session.commit()

    # Redirect to the plants page after adding the plant
    return redirect(url_for('plants'))


#for adding plants need to create javascript and connect to home.html where we can have add plants form

@app.route("/add_plant", methods=["GET", "POST"])
def add_plant_page():
    if request.method == "POST":  # Use Flask's request object
        name = request.form["name"]
        schedule = int(request.form["schedule"])
        user_id = session["user_id"]

        new_plant = Plant(name=name, schedule=schedule, user_id=user_id)
        db.session.add(new_plant)
        db.session.commit()
        return redirect("/my_plants")
    return render_template("add_plant.html")

@app.route("/edit_plant/<int:id>", methods=["GET", "POST"])
def edit_plant(id):
    plant = db.session.get(Plant, id)
    if not plant:
        return "Plant not found", 404

    if request.method == "POST":  # Use Flask's request object
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
        plant.completed()
        db.session.commit()
    return redirect("/my_plants/" + str(id))

api_key = "sk-mpir681573d064bfb10191"
def get_plant_info(query):
    url = f"https://perenual.com/api/species-list?key={api_key}&q={query}"
    response = http_requests.get(url)  # Corrected typo
    if response.status_code == 200:
        return response.json()
    return {"data": []}

def get_plant_details(id):
    url = f"https://perenual.com/api/species-care-guide-list?key={api_key}&species_id={id}"
    response = http_requests.get(url)
    if response.status_code == 200:
        return response.json()
    return {"data": []}

@app.route("/plant/<int:id>")
def plant_info(id):
    detail_data = get_plant_details(id)
    if "data" not in detail_data or not detail_data["data"]:
        return "No plant details found", 404

    plant = detail_data["data"][0]
    watering = "No info available."
    sunlight = "No info available."
    pruning = "No info available."

    for section in plant.get("section", []):
        if section["type"] == "watering":
            watering = section["description"]
        elif section["type"] == "sunlight":
            sunlight = section["description"]
        elif section["type"] == "pruning":
            pruning = section["description"]

    return render_template("plant_info.html", data=plant, watering=watering, sunlight=sunlight, pruning=pruning)

@app.route("/search_plant")
def search_plant():
    return render_template("search_plant.html")

@app.route("/results", methods=["POST"])
def results():
    query = request.form["query"]  # Use Flask's request object
    data = get_plant_info(query)
    return render_template("search_results.html", data=data, query=query)





@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = db.session.execute(db.select(User).where(User.username == username)).scalar()

        if existing_user:
            return "User already exists", 400
        new_user = User(username=username)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = db.session.execute(db.select(User).where(User.username == username)).scalar()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('plants'))
        return "Invalid credentials", 401

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))



if __name__ == "__main__":
    app.run(debug=True, port=8888)