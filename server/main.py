from flask import Flask, jsonify
from flask_cors import CORS
from db import db
from model import UserJobData, User
from flask import request
from flask_login import login_user
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from flask_login import logout_user
from password_validator import PasswordValidator
from flask_login import current_user
from dotenv import load_dotenv
import os
from gmailApi import run_gmail_scraper
import firebase_admin 
from firebase_admin import auth, credentials


load_dotenv()
app = Flask(__name__)
from flask_login import LoginManager


if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-adminsdk.json")  # <-- your service account key JSON
    firebase_admin.initialize_app(cred)
    
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

def get_firebase_uid():
    id_token = request.headers.get('Authorization')
    if not id_token:
        return None

    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token['uid']
    except Exception as e:
        print("Token verification failed:", e)
        return None

# to read exisitng entries
@app.route('/api/userApplicationData', methods=['GET'])
def get_applications():
    firebase_uid = get_firebase_uid()
    if not firebase_uid:
        return jsonify({"error": "Unauthorized"}), 401

    user = User.query.filter_by(firebase_uid=firebase_uid).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    applications = UserJobData.query.filter_by(user_id=user.id).all()
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
    uid = get_firebase_uid()

    if not uid:
        return jsonify({"error": "Unauthorized"}), 401
    
    user = User.query.filter_by(firebase_uid=uid).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json()
    new_app = UserJobData(
        company=data['company'],
        position=data['position'],
        status=data['status'],
        user_id=user.id,
        firebase_uid=user.firebase_uid
    )
    db.session.add(new_app)
    db.session.commit()
    return jsonify(message="Application created successfully", id=new_app.id), 201

# to delete data 
@app.route('/api/userApplicationData/<int:id>', methods=['DELETE'])
def delete_application(id):
    uid = get_firebase_uid()
    user = User.query.filter_by(firebase_uid=uid).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    app_row = UserJobData.query.filter_by(id=id, user_id=user.id).first()
    if not app_row:
        return jsonify({"error": "Not found or unauthorized"}), 404
    db.session.delete(app_row)
    db.session.commit()
    return jsonify(message="Deleted successfully")

@app.route('/api/userApplicationData/count', methods=['GET'])
def application_count():
    uid = get_firebase_uid()
    if not uid:
        return jsonify({"error": "Unauthorized"}), 401
    user = User.query.filter_by(firebase_uid=uid).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    count = UserJobData.query.filter_by(user_id=user.id).count()
    return jsonify({"count": count})

@app.route('/api/userApplicationData/interviewCount', methods=['GET'])
def get_interview_count():
    uid = get_firebase_uid()
    if not uid:
        return jsonify({"error": "Unauthorized"}), 401
    
    user = User.query.filter_by(firebase_uid=uid).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    count = UserJobData.query.filter_by(user_id=user.id, status='Interviewing').count()
    return jsonify({"interviewCount": count})

@app.route('/api/userApplicationData/offerCount', methods=['GET'])
def get_offer_count():
    uid = get_firebase_uid()
    if not uid:
        return jsonify({"error": "Unauthorized"}), 401
    
    user = User.query.filter_by(firebase_uid=uid).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    count = UserJobData.query.filter_by(user_id=user.id, status='Offer').count()
    return jsonify({"offerCount": count})


# to update entryes automaticly when chnge on frontend
@app.route('/api/userApplicationData/<int:id>', methods=['PUT'])
def update_application(id):
    uid = get_firebase_uid()
    user = User.query.filter_by(firebase_uid=uid).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    app_row = UserJobData.query.filter_by(id=id, user_id=user.id).first()

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

# we will connect the Gmail api. users need to connect their gmail first though 
@app.route('/api/connect-gmail', methods=['POST'])
def connect_gmail():
    try:
        data = request.json
        firebase_uid = data.get('uid')  # frontend must send { "uid": "..." }
        print("Firebase UID:", firebase_uid)
        applications = run_gmail_scraper(firebase_uid)
        return jsonify({"applications": applications}), 200
    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

# routing for the signup

@app.route('/api/signup', methods=['POST'])
def signup():
    id_token = request.headers.get('Authorization')
    if not id_token:
        return jsonify({"error": "Missing token"}), 401

    try:
        decoded_token = auth.verify_id_token(id_token)
        firebase_uid = decoded_token['uid']

        # Check if user already exists
        user = User.query.filter_by(firebase_uid=firebase_uid).first()
        if not user:
            user = User(firebase_uid=firebase_uid)
            db.session.add(user)
            db.session.commit()

        return jsonify({'message': 'Signup successful'}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': 'Invalid token'}), 401
    

## verifying auth
@app.route('/api/authcheck', methods=['GET'])
def checkauth():
    id_token = request.headers.get('Authorization')

    if not id_token:
        return jsonify({"authenticated": False, "error": "No token provided"}), 401

    try:
        decoded_token = auth.verify_id_token(id_token)
        user_email = decoded_token['email']
        print("✅ Verified Firebase user:", user_email)
        return jsonify({"authenticated": True, "email": user_email}), 200
    except Exception as e:
        print("❌ Token verification failed:", e)
        return jsonify({"authenticated": False, "error": str(e)}), 401
    


#sign out 
@app.route('/api/signout', methods=['GET'])
def signout():
    response = jsonify({"message": "Signed out successfully."})
    response.set_cookie('session', '', expires=0)  # Clear any session cookie if you're using one
    return response, 200

def get_firebase_uid():
    id_token = request.headers.get('Authorization')
    if not id_token:
        return None
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token['uid']
    except Exception as e:
        print("❌ Token verification failed:", e)
        return None

if __name__ == "__main__":
    app.run(debug=True, port=8080)
    