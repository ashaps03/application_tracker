from flask import Flask, jsonify
from flask_cors import CORS
from db import db
from model import UserJobData
from flask import request
from flask_login import login_user
from model import User
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from flask_login import logout_user
from password_validator import PasswordValidator
from flask_login import current_user
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.init_app(app)

#userr loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)

##steps to create teh database, create db file, creae model, initiate database and configure in main, create the route fro teh database
## configureing SQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///UserJobData.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Initialize the database
db.init_app(app)
# Create tables
with app.app_context():
    db.create_all()
## now need to create the isntance using the python shell by simply running this file so python3 main.py

# to read exisitng entries
@app.route('/api/userApplicationData', methods=['GET'])
def get_applications():
    if not current_user.is_authenticated:
        return jsonify({"error", "Unauhorized"}), 401
    applications = UserJobData.query.filter_by(user_id=current_user.id).all()
    result = [{
        "id": app.id,
        "company": app.company,
        "position": app.position,
        "status": app.status
    } for app in applications]
    return jsonify(result)

# to creaete a ne entry
@app.route('/api/userApplicationData', methods=['POST'])
def create_application():
    if not current_user.is_authenticated:
        return jsonify({"error","Unauhorized"}), 401
    data = request.get_json()
    new_app = UserJobData(
        company=data['company'],
        position=data['position'],
        status=data['status'],
        user_id=current_user.id
    )
    db.session.add(new_app)
    db.session.commit()
    return jsonify(message="Application created successfully", id=new_app.id), 201

# to delete data 
@app.route('/api/userApplicationData/<int:id>', methods=['DELETE'])
def delete_application(id):
    if not current_user.is_authenticated:
        return jsonify({"error","Not found or unauthorized"}), 404
    app_row = UserJobData.query.filter_by(id=id, user_id=current_user.id).first()
    if not app_row:
        return jsonify({"error": "Not found or unauthorized"}), 404
    db.session.delete(app_row)
    db.session.commit()
    return jsonify(message="Deleted successfully")

@app.route('/api/userApplicationData/count', methods=['GET'])
def application_count():
    if not current_user.is_authenticated:
        return jsonify({"error","Unauthorized"}), 401

    count = UserJobData.query.filter_by(user_id=current_user.id).count()
    return jsonify({"count": count})

@app.route('/api/userApplicationData/interviewCount', methods=['GET'])
def get_interview_count():
    if not current_user.is_authenticated:
        return jsonify({"error","Unauthorized"}), 401

    count = UserJobData.query.filter_by(user_id=current_user.id, status='Interviewing').count()
    return jsonify({"interviewCount": count})

@app.route('/api/userApplicationData/offerCount', methods=['GET'])
def get_offer_count():
    if not current_user.is_authenticated:
        return jsonify({"error","Unauthorized"}), 401
    
    count= UserJobData.query.filter_by(user_id=current_user.id, status='Offer').count()
    return jsonify({"offerCount": count})


# to update entryes automaticly when chnge on frontend
@app.route('/api/userApplicationData/<int:id>', methods=['PUT'])
def update_application(id):
    if not current_user.is_authenticated:
        return jsonify({"error","Unauthorized"}), 401
    
    app_row = UserJobData.query.filter_by(id=id, user_id=current_user.id).first()

    if not app_row:
        return jsonify({"error": "Not found or unauthorized"}), 404

    data = request.get_json()  # Receives updated fields from frontend

    # Update the row fields
    app_row.company = data['company']
    app_row.position = data['position']
    app_row.status = data['status']
    db.session.commit()  # Saves the updated row to your actual database (e.g. UserJobData.db)

    return jsonify(message="Updated successfully")

# trsting api GET functionality (can remove later)
@app.route("/api/users", methods=['GET'])
def users():
    return jsonify(
        {
            "users": [
                'Samantha',
                'Ashley',
                'Jessie'
            ]
        }
    )

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

#  password rules 
schema = PasswordValidator()
schema \
    .min(8) \
    .max(100) \
    .has().uppercase() \
    .has().lowercase() \
    .has().digits() \
    .has().no().spaces()

## creating the routing fro the signup
@app.route('/api/signup', methods= ['POST'])
def signup():
    data= request.get_json()
    name= data.get('name')
    email= data.get('email')
    password= data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    if not schema.validate(password):
        return jsonify({"error": "Password must be 8+ characters and include upper, lower, number, and no spaces"}), 400

    hashed_pw = generate_password_hash(password, method="pbkdf2:sha256")
    new_user = User(name=name, email=email, password=hashed_pw)

    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)
    return jsonify({"message": "User created", "user_id": new_user.id}), 201

## creating the routing fro the signup
@app.route('/api/signout', methods=['GET'])
def signout():
    logout_user()
    return jsonify({"Message":"Logged out sucessfully"})

    

## creating the routing fro the login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    name= data.get('name')
    email=data.get('email')
    password= data.get('password')

    user = User.query.filter_by(email=email).first()
    
    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "invalid email or password"}), 401
    
    login_user(user)

    return jsonify({"message": "Login successful", "user_id": user.id})




if __name__ == "__main__":
    app.run(debug=True, port=8080)
    