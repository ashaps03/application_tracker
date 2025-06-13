from flask import Flask, jsonify
from flask_cors import CORS
from db import db
from model import UserJobData

app = Flask(__name__)
cors = CORS(app, origins='*')

##steps to create teh database, create db file, creae model, initiate database and configure in main, create the route fro teh database
## configureing SQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///UserJobData.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Initialize the database
db.init_app(app)
# Create tables
with app.app_context():
    db.create_all()
## now need to create the isntance using the python shell, commands = 

@app.route("/api/userApplicationData", methods=['GET'])
def get_user_application_data():
    apps = UserJobData.query.all()
    result = [
        {
            "id": app.id,
            "company": app.company,
            "position": app.position,
            "status": app.status
        }
        for app in apps
    ]
    return jsonify(result)

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
    