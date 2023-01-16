
from flask import Flask
from pymongo import MongoClient
import hashlib
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
import datetime
import hashlib
import urllib
import secrets

app = Flask(__name__)
jwt = JWTManager(app) # initialize JWTManager

my_secret = secrets.token_hex(16)
print(my_secret)

app.config['JWT_SECRET_KEY'] = my_secret
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1) # define the life span of the token

client = MongoClient("mongodb+srv://Sohaib:sohaib@cluster0.ljdhvgj.mongodb.net/?retryWrites=true&w=majority")
db = client["mydatabase"]
users_collection = db["users"]
templates_collection = db["templates"]

@app.route('/')
def hello_world():
	return 'Hello, World!'

@app.route("/api/v1/users", methods=["POST"])
def register():
    new_user = request.get_json() # store the json body request
    # Creating Hash of password to store in the database
    new_user["password"] = hashlib.sha256(new_user["password"].encode("utf-8")).hexdigest() # encrpt password
    # Checking if user already exists
    doc = users_collection.find_one({"username": new_user["username"]}) # check if user exist
    # If not exists than create one
    if not doc:
        # Creating user
        users_collection.insert_one(new_user)
        return jsonify({'msg': 'User created successfully'}), 201
    else:
        return jsonify({'msg': 'Username already exists'}), 409

@app.route("/api/v1/login", methods=["post"])
def login():
    # Getting the login Details from payload
    login_details = request.get_json() # store the json body request
    # Checking if user exists in database or not
    user_from_db = users_collection.find_one({'username': login_details['username']})  # search for user in database
    # If user exists
    if user_from_db:
        # Check if password is correct
        encrpted_password = hashlib.sha256(login_details['password'].encode("utf-8")).hexdigest()
        if encrpted_password == user_from_db['password']:
            # Create JWT Access Token
            access_token = create_access_token(identity=user_from_db['username']) # create jwt token
            # Return Token
            return jsonify(access_token=access_token), 200
    return jsonify({'msg': 'The username or password is incorrect'}), 401

@app.route("/create", methods=["POST"])
@jwt_required()
def create_template():
    """Creating the template with respect to the user
    Returns:
        dict: Return the profile and template created
    """
    # Getting the user from access token
    current_user = get_jwt_identity() # Get the identity of the current user
    user_from_db = users_collection.find_one({'username' : current_user})
    
    # Checking if user exists
    if user_from_db:
        # Getting the template details from json
        template_details = request.get_json() # store the json body request
        # Viewing if templated already present in collection
        user_template = {'profile' : user_from_db["username"],  "template": template_details["template"]}
        doc = templates_collection.find_one(user_template) # check if user exist
        # Creating collection if not exists
        
        if not doc:
            templates_collection.insert_one(user_template)
            print("user_template ", user_template)
            return jsonify({'msg': 'Template created successfully'}), 200
        # Returning message if template exists
        else: return jsonify({'msg': 'Template already exists on your profile'}), 404
    else:
        return jsonify({'msg': 'Access Token Expired'}), 404

@app.route("/get", methods=["GET"])
@jwt_required()
def get_template():
    """Get the templates of specefic user
    Returns:
        dict: Return the profile and template 
    """
    # Getting the user from access token
    current_user = get_jwt_identity() # Get the identity of the current user
    user_from_db = users_collection.find_one({'username' : current_user})
    # Checking if user exists
    if user_from_db:
        # Viewing if templated already present in collection
        user_template = {'profile' : user_from_db["username"]}
        return jsonify({"docs":list(db.templates.find(user_template, {"_id":0}))}), 200
    else:
        return jsonify({'msg': 'Access Token Expired'}), 404

@app.route("/update", methods=["POST"])
@jwt_required()
def update_template():
    """Updating the template with respect to the user
    Returns:
        dict: Return the profile and template created
    """
    # Getting the user from access token
    current_user = get_jwt_identity() # Get the identity of the current user
    user_from_db = users_collection.find_one({'username' : current_user})
    
    # Checking if user exists
    if user_from_db:
        # Getting the template details from json
        template_details = request.get_json() # store the json body request
        # Viewing if templated already present in collection
        user_template = {'profile' : user_from_db["username"],  "template": template_details["old_template"]}
        doc = templates_collection.find_one(user_template) # check if user exist
        # Updating collection if not exists
        
        if doc:
            doc["template"] = template_details["new_template"]
            templates_collection.update_one(user_template, {"$set": {"template":doc["template"]}}, upsert=False)
            return jsonify({'msg': 'Template Updated successfully'}), 200
        # Returning message if template exists
        else: return jsonify({'msg': 'Template not exists on your profile'}), 404
    else:
        return jsonify({'msg': 'Access Token Expired'}), 404

@app.route("/delete", methods=["POST"])
@jwt_required()
def delete_template():
    """Creating the template with respect to the user
    Returns:
        dict: Return the profile and template created
    """
    # Getting the user from access token
    current_user = get_jwt_identity() # Get the identity of the current user
    user_from_db = users_collection.find_one({'username' : current_user})
    
    # Checking if user exists
    if user_from_db:
        # Getting the template details from json
        template_details = request.get_json() # store the json body request
        # Viewing if templated already present in collection
        user_template = {'profile' : user_from_db["username"],  "template": template_details["template"]}
        doc = templates_collection.find_one(user_template) # check if user exist
        # Creating collection if not exists
        
        if doc:
            templates_collection.delete_one(user_template)
            print("user_template ", user_template)
            return jsonify({'msg': 'Template Deleted Sucessfully'}), 404
        # Returning message if template exists
        else: return jsonify({'msg': 'Template not exists on your profile'}), 404
    else:
        return jsonify({'msg': 'Access Token Expired'}), 404

import json
from flask import Flask
from main import app

def test_flask():
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    flask_app =  app
    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as test_client:
        response = test_client.get('/')
        assert response.status_code == 200
       
def test_registration():
    flask_app =  app
    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as test_client:
        data = {
            "username":"test1",
            "password":"1234"
        }
        response = test_client.post('/api/v1/users', data=json.dumps(data), headers={"Content-Type": "application/json"})
        assert response.status_code == 201 or response.status_code == 409
def test_login():
    flask_app =  app
    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as test_client:
        data = {
            "username":"test1",
            "password":"1234"
        }
        response = test_client.post('/api/v1/login', data=json.dumps(data), headers={"Content-Type": "application/json"})
        assert response.status_code == 200

