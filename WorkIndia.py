#!/usr/bin/env python
# coding: utf-8

# In[2]:


get_ipython().system('pip install flask flask-jwt-extended flask-sqlalchemy flask-bcrypt')


# In[3]:


from flask_jwt_extended import jwt_required, get_jwt_identity


# In[4]:


@app.route("/book-seat", methods=["POST"])
@jwt_required()
def book_seat():
    user_id = get_jwt_identity() 
    data = request.json
    train = Train.query.get(data["train_id"])
    if train and train.available_seats > 0:
        train.available_seats -= 1
        booking = Booking(user_id=user_id, train_id=train.id, status="booked")
        db.session.add(booking)
        db.session.commit()
        return jsonify({"message": "Seat booked successfully"}), 200
    return jsonify({"error": "No seats available"}), 400


# In[ ]:


from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config.from_object(Config)
jwt = JWTManager(app)


# In[ ]:


import os

class Config:
    SECRET_KEY = "your_secret_key"
    JWT_SECRET_KEY = "your_jwt_secret_key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///railway.db"  
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_API_KEY = "your_admin_api_key"


# In[ ]:


from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import Flask

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), nullable=False)  

class Train(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    train_name = db.Column(db.String(120), nullable=False)
    source = db.Column(db.String(80), nullable=False)
    destination = db.Column(db.String(80), nullable=False)
    total_seats = db.Column(db.Integer, nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    train_id = db.Column(db.Integer, db.ForeignKey("train.id"), nullable=False)
    status = db.Column(db.String(10), nullable=False)  # 'booked' or 'canceled'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# In[ ]:


from flask import request, jsonify
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask_jwt_extended import JWTManager

jwt = JWTManager(app)

def verify_api_key(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get("API-Key")
        if api_key == Config.ADMIN_API_KEY:
            return func(*args, **kwargs)
        return jsonify({"error": "Unauthorized"}), 403
    return wrapper

def jwt_required_user(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims["role"] == "user":
            return func(*args, **kwargs)
        return jsonify({"error": "Access denied"}), 403
    return wrapper


# In[ ]:


from flask import request, jsonify

@app.route("/admin/add-train", methods=["POST"])
@verify_api_key
def add_train():
    data = request.json
    train = Train(
        train_name=data["train_name"],
        source=data["source"],
        destination=data["destination"],
        total_seats=data["total_seats"],
        available_seats=data["total_seats"]
    )
    db.session.add(train)
    db.session.commit()
    return jsonify({"message": "Train added successfully"}), 201

@app.route("/trains", methods=["GET"])
def get_trains():
    source = request.args.get("source")
    destination = request.args.get("destination")
    trains = Train.query.filter_by(source=source, destination=destination).all()
    response = [{"id": t.id, "name": t.train_name, "seats_available": t.available_seats} for t in trains]
    return jsonify(response)

@app.route("/book-seat", methods=["POST"])
@jwt_required()
def book_seat():
    user_id = get_jwt_identity()
    data = request.json
    train = Train.query.get(data["train_id"])
    if train and train.available_seats > 0:
        train.available_seats -= 1
        booking = Booking(user_id=user_id, train_id=train.id, status="booked")
        db.session.add(booking)
        db.session.commit()
        return jsonify({"message": "Seat booked successfully"}), 200
    return jsonify({"error": "No seats available"}), 400

@app.route("/booking-details", methods=["GET"])
@jwt_required()
def booking_details():
    user_id = get_jwt_identity()
    bookings = Booking.query.filter_by(user_id=user_id).all()
    response = [{"train_id": b.train_id, "status": b.status, "timestamp": b.timestamp} for b in bookings]
    return jsonify(response)


# In[ ]:


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=False, use_reloader=False)  


# In[6]:


get_ipython().system('pip install requests')


# In[10]:


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# Configuration
class Config:
    SECRET_KEY = "your_secret_key"
    JWT_SECRET_KEY = "your_jwt_secret_key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///railway.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
jwt = JWTManager(app)


# In[1]:


pip install waitress


# In[1]:


from waitress import serve

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  
    serve(app, host="0.0.0.0", port=8000)


# In[ ]:


import requests

url = "http://127.0.0.1:5000/admin/add-train"
headers = {
    "API-Key": "your_admin_api_key",
    "Content-Type": "application/json"
}
data = {
    "train_name": "Express Train",
    "source": "A",
    "destination": "B",
    "total_seats": 100
}

response = requests.post(url, headers=headers, json=data)
print(response.status_code)
print(response.json())


# In[ ]:


url = "http://127.0.0.1:5000/book-seat"
headers = {
    "Authorization": "Bearer your_jwt_token",
    "Content-Type": "application/json"
}
data = {
    "train_id": 1  
}

response = requests.post(url, headers=headers, json=data)
print(response.status_code)
print(response.json())


# In[ ]:


from waitress import serve

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  
    serve(app, host="0.0.0.0", port=8000)


# In[ ]:


# Ensure app is defined
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

class Config:
    SECRET_KEY = "your_secret_key"
    JWT_SECRET_KEY = "your_jwt_secret_key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///railway.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
jwt = JWTManager(app)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  
    app.run(debug=False, use_reloader=False)


# In[ ]:





# In[9]:


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  
    app.run(debug=False, use_reloader=False)  


# In[7]:


import requests

url = "http://127.0.0.1:5000/admin/add-train"
headers = {
    "API-Key": "your_admin_api_key",
    "Content-Type": "application/json"
}
data = {
    "train_name": "Express Train",
    "source": "A",
    "destination": "B",
    "total_seats": 100
}

response = requests.post(url, headers=headers, json=data)
print(response.status_code)
print(response.json())


# In[8]:


url = "http://127.0.0.1:5000/trains"
params = {
    "source": "A",
    "destination": "B"
}

response = requests.get(url, params=params)
print(response.status_code)
print(response.json())


# In[5]:


curl -X POST http://127.0.0.1:5000/admin/add-train \
-H "API-Key: your_admin_api_key" \
-H "Content-Type: application/json" \
-d '{"train_name": "Express", "source": "A", "destination": "B", "total_seats": 100}'


# In[ ]:


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

class Config:
    SECRET_KEY = "your_secret_key"
    JWT_SECRET_KEY = "your_jwt_secret_key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///railway.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
jwt = JWTManager(app)


# In[ ]:


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  
    app.run(debug=False, use_reloader=False)


# In[ ]:


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from waitress import serve

class Config:
    SECRET_KEY = "your_secret_key"
    JWT_SECRET_KEY = "your_jwt_secret_key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///railway.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
jwt = JWTManager(app)

if __name__ == "__main__":
    with app.app_context():
        db.create_all() 
    serve(app, host="0.0.0.0", port=8000)


# In[ ]:


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

class Config:
    SECRET_KEY = "your_secret_key"
    JWT_SECRET_KEY = "your_jwt_secret_key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///railway.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
jwt = JWTManager(app)


# In[ ]:


from app import app, db
from waitress import serve

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  
    serve(app, host="0.0.0.0", port=8000)


# In[ ]:


Serving on http://0.0.0.0:8000


# In[ ]:


curl http://127.0.0.1:8000


# In[ ]:


curl -X POST http://127.0.0.1:8000/admin/add-train \
     -H "API-Key: your_admin_api_key" \
     -H "Content-Type: application/json" \
     -d '{"train_name": "Express Train", "source": "A", "destination": "B", "total_seats": 100}'


# In[ ]:


import requests

url = "http://127.0.0.1:8000/admin/add-train"
headers = {
    "API-Key": "your_admin_api_key",
    "Content-Type": "application/json"
}
data = {
    "train_name": "Express Train",
    "source": "A",
    "destination": "B",
    "total_seats": 100
}

response = requests.post(url, headers=headers, json=data)
print("Status Code:", response.status_code)
print("Response JSON:", response.json())


# In[ ]:


import requests

url = "http://127.0.0.1:8000/admin/add-train"  
headers = {
    "API-Key": "your_admin_api_key",  
    "Content-Type": "application/json"
}
data = {
    "train_name": "Express Train",
    "source": "A",
    "destination": "B",
    "total_seats": 100
}

try:
    response = requests.post(url, headers=headers, json=data)
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())
except requests.ConnectionError:
    print("Error: Could not connect to the server. Ensure the server is running and accessible.")
except Exception as e:
    print(f"An error occurred: {e}")


# In[ ]:




