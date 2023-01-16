
from flask import Flask, request 
from flask_pymongo import PyMongo
from flask_restful import Resource, Api
from bson.objectid import ObjectId
from cerberus import Validator
import secrets, datetime, hashlib
from flask_jwt_extended import JWTManager, create_access_token


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/practise"
mongo = PyMongo(app)
api = Api(app)


my_secret = secrets.token_hex(16)
print(my_secret)
app.config['JWT_SECRET_KEY'] = my_secret
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
jwt = JWTManager(app)


@app.route("/register", methods=["POST"])
def register():
    new_user = request.get_json()
    new_user["password"] = hashlib.sha256(new_user["password"].encode("utf-8")).hexdigest()
    doc = mongo.db.register.find_one({"username": new_user["username"]})

    if not doc:
        mongo.db.register.insert_one(new_user)
        return {'msg': 'User created successfully'}, 201
    else:
        return {'msg': 'Username already exists'}, 409


@app.route("/login", methods=["POST"])
def login():
    login_details = request.get_json()
    user_from_db = mongo.db.register.find_one({'username': login_details['username']})

    if user_from_db:
        encrpted_password = hashlib.sha256(login_details['password'].encode("utf-8")).hexdigest()
        if encrpted_password == user_from_db['password']:
            access_token = create_access_token(identity=user_from_db['username'])
            return access_token, 200
    return {'msg': 'The username or password is incorrect'}, 401


@app.route("/fetch_all")
def fetch_all():
    result = mongo.db.register.find({})
    data = []

    for row in result:
        temp = {}
        temp["_id"] = str(row["_id"])
        temp["username"] = row['username']
        temp["password"] = row["password"]

        data.append(temp)
    return data,200


@api.resource('/user', endpoint="users")
class UserList(Resource):
    def get(self):
        result = mongo.db.user.find({})
        data = []
    
        for row in result:
            temp = {}
            temp["_id"] = str(row["_id"])
            temp["name"] = row['name']
            temp["age"] = row["age"]
            temp["salary"] = row['salary']

            data.append(temp)
        return data,200


    def post(self):
        try:
            data = request.get_json()
            temp = {
                "name":data.get('name'),
                "age":data.get("age"),
                "salary":data.get("salary"),
            }

            Schema = {'name': {'required': True, 'type': 'string'}, 
            'age': {'type': 'integer', 'min': 18, 'max': 30},
            'salary':{'type':'number'}}

            v = Validator(Schema)

            if v.validate(temp):
                _id = mongo.db.user.insert_one(temp)
            else:
                _id = None

            return {"status":"OK","_id":str(_id)},201

        except Exception as e:
            return {"status":"error","message":str(e)},400


@api.resource('/user/<id>', endpoint="user")
class User(Resource):
    def get(self, id):
        try:
            result = mongo.db.user.find_one({"_id":ObjectId(id)})
            
            temp = {}
            temp["_id"] = str(result["_id"])
            temp["name"] = result['name']
            temp["age"] = result['age']
            temp["salary"] = result['salary']

            return temp,200

        except Exception as e:
            return {"status":"error","message":str(e)},400

    def put(self, id):
        data = request.get_json()

        temp = {
                "name":data.get('name'),
                "age":data.get("age"),
                "salary":data.get("salary"),
            }

        Schema = {'name': {'required': True, 'type': 'string'}, 
            'age': {'type': 'integer', 'min': 18, 'max': 30},
            'salary':{'type':'number'}}

        v = Validator(Schema)

        if v.validate(temp):
            mongo.db.user.update_one({"_id":ObjectId(id)}, {"$set": temp}) 
            result = mongo.db.user.find_one({"_id":ObjectId(id)})

            temp = {}
            temp["_id"] = str(result["_id"])
            temp["name"] = result['name']
            temp["age"] = result['age']
            temp["salary"] = result['salary']

            return temp,202
        else:
            return {'status':'error'},400

    def delete(self, id):
        result = mongo.db.user.find_one({"_id":ObjectId(id)})
        if result == None:
            return {'status':'error'},400
        else:
            mongo.db.user.delete_one({"_id": ObjectId(id)})
            return {"status":"OK"},200


if __name__ == '__main__':
    app.run(debug=True)
