
# pip install Flask-PyMongo
# https://stackabuse.com/stringegrating-mongodb-with-flask-using-flask-pymongo/

from flask import Flask, render_template, jsonify, request
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
        {'_id': 1, 'title': "todo title one ", 'body': "todo body one "},
        {'_id': 2, 'title': "todo title two", 'body': "todo body two"},
        {'_id': 3, 'title': "todo title three", 'body': "todo body three"},
        {'_id': 4, 'title': "todo title four", 'body': "todo body four"},
        {'_id': 5, 'title': "todo title five", 'body': "todo body five"},
        ])
    return jsonify(message="success")

@app.route("/")
def home():
    todos = db.todos.find()
    return jsonify([todo for todo in todos])

@app.route("/get_todo/<string:todoId>")
def insert_one(todoId):
    todo = db.todos.find_one({"_id": todoId})
    return jsonify(message=todo)

@app.route("/replace_todo/<string:todoId>")
def replace_one(todoId):
    result = db.todos.replace_one({'_id': todoId}, {'title': "modified title"})
    return {'id': result.raw_result}

@app.route("/update_todo/<string:todoId>")
def update_one(todoId):
    result = db.todos.update_one({'_id': todoId}, {"$set": {'title': "updated title"}})
    return result.raw_result

@app.route('/update_many')
def update_many():
    todo = db.todos.update_many({'title' : 'todo title two'}, {"$set": {'body' : 'updated body'}})
    return todo.raw_result

@app.route("/delete_todo/<string:todoId>", methods=['DELETE'])
def delete_todo(todoId):
    todo = db.todos.find_one_and_delete({'_id': todoId})
    if todo is not None:
        return todo.raw_result
    return "ID does not exist"

@app.route('/delete_many', methods=['DELETE'])
def delete_many():
    todo = db.todos.delete_many({'title': 'todo title two'})
    return todo.raw_result

@app.route("/save_file", methods=['POST', 'GET'])
def save_file():
    upload_form = """<h1>Save file</h1>
                     <form method="POST" enctype="multipart/form-data">
                     <input type="file" name="file" id="file">
                     <br><br>
                     <input type="submit">
                     </form>"""
                     
    if request.method=='POST':
        if 'file' in request.files:
            file = request.files['file']
            mongo.save_file(file.filename, file)
            return {"file name": file.filename}
    return upload_form

@app.route("/get_file/<filename>")
def get_file(filename):
    return mongo.send_file(filename)

if __name__ == '__main__':
    app.run(debug=True)