from flask import Flask, jsonify
from flask_cors import CORS
from db import db
from model import UserJobData
from flask import request


app = Flask(__name__)
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
    applications = UserJobData.query.all()
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
    data = request.get_json()
    new_app = UserJobData(
        company=data['company'],
        position=data['position'],
        status=data['status']
    )
    db.session.add(new_app)
    db.session.commit()
    return jsonify(message="Application created successfully", id=new_app.id), 201

# to delete data 
@app.route('/api/userApplicationData/<int:id>', methods=['DELETE'])
def delete_application(id):
    app_row = UserJobData.query.get_or_404(id)
    db.session.delete(app_row)
    db.session.commit()
    return jsonify(message="Deleted successfully")

@app.route('/api/userApplicationData/count', methods=['GET'])
def application_count():
    count = UserJobData.query.count()
    return jsonify({"count": count})

@app.route('/api/userApplicationData/interviewCount', methods=['GET'])
def get_interview_count():
    count =UserJobData.query.filter_by(status='Interviewing').count()
    return jsonify({"interviewCount": count})







@app.route('/api/userApplicationData/offerCount', methods=['GET'])
def get_offer_count():
    count= UserJobData.query.filter_by(status= 'Offer').count()
    return jsonify({"offerCount": count})


# to update entryes automaticly when chnge on frontend
@app.route('/api/userApplicationData/<int:id>', methods=['PUT'])
def update_application(id):
    data = request.get_json()  # Receives updated fields from frontend
    app_row = UserJobData.query.get_or_404(id)  # Finds the row by ID in your database

    # Update the row fields
    app_row.company = data['company']
    app_row.position = data['position']
    app_row.status = data['status']

    db.session.commit()  # 🔥 Saves the updated row to your actual database (e.g. UserJobData.db)

    return jsonify(message="Updated successfully")



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
if __name__ == "__main__":
    app.run(debug=True, port=8080)
    