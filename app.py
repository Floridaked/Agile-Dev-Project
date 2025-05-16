from flask import *
from pathlib import Path
from db import db
from models import *
from models.user import User, Achievement
from datetime import datetime as dt, timedelta
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
    session.clear()
    return render_template("home.html")

@app.route("/my_plants")
def plants():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    user = User.query.get(user_id)
    if not user:
        session.clear() 
        return redirect(url_for('login'))
 

    user_id = session["user_id"]
    user = db.session.get(User, user_id)

    # Fetch all plants for the user
    plants = db.session.query(Plant).filter_by(user_id=user_id).all()
    print(f"Plants for user {user_id}: {plants}")  # Debug: Print the plants list

    sad_plant_found = False  # Flag to track if any plant is sad

    for plant in plants:
        try:
            plant.countdown = plant.count_down()  # Call the count_down method
        except Exception as e:
            print(f"Error calculating countdown for plant {plant.name}: {e}")
            plant.countdown = None  # Assign None if an error occurs
    
    plants = sorted(plants, key=lambda p: p.countdown)

    # Reset day streak if any plant is sad
    if sad_plant_found:
        print(f"Sad plant found for user {user_id}. Resetting day streak.")
        user.day_streak = 0
        db.session.commit()

    # Check the total number of plants added by the user
    total_plants = len(plants)
    print(f"Total plants for user {user_id}: {total_plants}")  # Debug

    # Define plant addition thresholds
    plant_medal = None
    if total_plants == 3:
        plant_medal = "Bronze Planter"
    elif total_plants == 5:
        plant_medal = "Silver Planter"
    elif total_plants == 10:
        plant_medal = "Gold Planter"

    # Reward the user if they qualify
    if plant_medal:
        # Check if the user already has this medal
        existing_medal = db.session.query(Achievement).filter_by(user_id=user_id, medal=plant_medal).first()
        if not existing_medal:
            new_achievement = Achievement(user_id=user_id, medal=plant_medal)
            db.session.add(new_achievement)
            db.session.commit()
            flash(f"Congratulations! You've earned a {plant_medal} medal for adding {total_plants} plants!", "plant_streak")

    return render_template("plants.html", data=plants, user=user)

@app.route("/my_plants/<int:id>") 
def plant_detail(id):   
    if 'user_id' not in session:
        return redirect(url_for('login'))
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
    plant_type = request.form["plant_type"]
    first_watered =  request.form["first_watered"]
    first_watered = dt.strptime(first_watered, "%Y-%m-%d").strftime("%B %d, %Y") + " at 12:00AM"    
    new_plant = Plant(name=name, schedule=int(schedule), user_id=session['user_id'], plant_type=plant_type)
    first_watering_record = Complete(plant=new_plant, date=first_watered)
    db.session.add(new_plant)
    db.session.add(first_watering_record)
    db.session.commit()

    # Redirect to the plants page after adding the plant
    return redirect(url_for('plants'))

#for adding plants need to create javascript and connect to home.html where we can have add plants form
@app.route("/add_plant", methods=["GET", "POST"])
def add_plant_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == "POST":
        name = request.form["name"]
        schedule = int(request.form["schedule"])
        plant_type = request.form["plant_type"]
        first_watered = request.form["first_watered"]
        first_watered = dt.strptime(first_watered, "%Y-%m-%d").strftime("%B %d, %Y") + " at 12:00AM"
        user_id = session["user_id"]

        # Add the new plant
        new_plant = Plant(name=name, schedule=schedule, user_id=user_id, plant_type=plant_type)
        first_watering_record = Complete(plant=new_plant, date=first_watered)
        db.session.add(new_plant)
        db.session.add(first_watering_record)
        db.session.commit()


        return redirect("/plants")
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

@app.route("/achievements")
def achievements():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    achievements = db.session.execute(db.select(Achievement).where(Achievement.user_id == user_id)).scalars().all()

    # Sort achievements by the first letter of the second word in the medal name
    achievements = sorted(achievements, key=lambda a: a.medal.split()[1][0])

    return render_template("achievement.html", achievements=achievements)

@app.route("/watered/<int:id>", methods=["POST"])
def water_plant(id):
    # Check if the user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Get the plant
    stmt = db.select(Plant).where(Plant.id == id)
    plant = db.session.execute(stmt).scalar()

    if plant:
        plant.completed()
        db.session.commit()

        # Get the user
        user = db.session.get(User, session['user_id'])
        if not user:
            return redirect(url_for('login'))

        # Increment the user's streak
        user.water_streak += 1

                # Update the day streak
        today = dt.now().date()
        if user.last_active_date == today:
            # User already active today, no change to streak
            pass
        elif user.last_active_date == today - timedelta(days=1):
            # Increment streak if last active date was yesterday
            user.day_streak += 1
        else:
            # Reset streak if last active date was not yesterday
            user.day_streak = 1

        user.last_active_date = today
        db.session.commit()

        # Check if the user qualifies for a day streak medal
        day_streak_medal = None
        if user.day_streak == 90:  # 3 months
            day_streak_medal = "Gold Streaker"
        elif user.day_streak == 30:  # 1 month
            day_streak_medal = "Silver Streaker"
        elif user.day_streak == 7:  # 7 days
            day_streak_medal = "Bronze Streaker"

        if day_streak_medal:
            # Save the medal to the Achievement table
            existing_medal = db.session.query(Achievement).filter_by(user_id=user.id, medal=day_streak_medal).first()
            if not existing_medal:
                new_achievement = Achievement(user_id=user.id, medal=day_streak_medal)
                db.session.add(new_achievement)
                db.session.commit()

                flash(f"Congratulations! You've earned a {day_streak_medal} medal for maintaining a {user.day_streak}-day streak!", "day_streak")


        # Check if the user qualifies for a reward
        medal = None
        if user.water_streak == 10:
            medal = "Gold Waterer"
        elif user.water_streak == 5:
            medal = "Silver Waterer"
        elif user.water_streak == 3:
            medal = "Bronze Waterer"

        if medal:
            # Save the medal to the Achievement table
            new_achievement = Achievement(user_id=user.id, medal=medal)
            db.session.add(new_achievement)
            db.session.commit()

            flash(f"Congratulations! You've earned a {medal} medal for watering your plant {user.water_streak} times", "water_streak")

    return redirect("/my_plants/" + str(id))

api_key = os.getenv("API_KEY")

def get_plant_info(query):
    url = f"https://perenual.com/api/species-list?key={api_key}&q={query}"
    response = http_requests.get(url) 
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
    if 'user_id' not in session:
        return redirect(url_for('login'))
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
    query = ""
    data = get_plant_info(query)

    def get_common_name(plant):
        return plant.get("common_name", "").lower()

    if "data" in data and isinstance(data["data"], list):
        data["data"] = sorted(data["data"], key=get_common_name)

    return render_template("search_plant.html", data=data)

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
        
        # Successful login
        session['user_id'] = user.id
        session['username'] = user.username
        return redirect(url_for('plants'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True, port=8888)