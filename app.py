
# pip install Flask-PyMongo
# https://stackabuse.com/integrating-mongodb-with-flask-using-flask-pymongo/

from flask import Flask, render_template, jsonify
from flask_pymongo import PyMongo
import json

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/todo_db"
mongo = PyMongo(app)
db = mongo.db

@app.route("/add_one")
def add_one():
    db.todos.insert_one({'title': "todo title", 'body': "todo body"})
    return jsonify(message="success")

@app.route("/add_many")
def add_many():
    db.todos.insert_many([
        {'title': "todo title one ", 'body': "todo body one "},
        {'title': "todo title two", 'body': "todo body two"},
        {'title': "todo title three", 'body': "todo body three"},
        {'title': "todo title four", 'body': "todo body four"},
        {'title': "todo title five", 'body': "todo body five"},
        {'title': "todo title six", 'body': "todo body six"},
        ])
    return jsonify(message="success")

@app.route("/")
def home():
    todos = db.todos.find()
    return json.loads(json.dumps(todos))

@app.route("/get_todo/<string:todoId>")
def insert_one(todoId):
    todo = db.todos.find_one({"_id": todoId})
    return jsonify(message=todo)

@app.route("/user/<username>")
def user_profile(username):
    return render_template("user.html", 
                            user=username)

if __name__ == '__main__':
    app.run(debug=True)