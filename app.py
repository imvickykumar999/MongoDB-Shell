
# pip install Flask-PyMongo
# https://stackabuse.com/stringegrating-mongodb-with-flask-using-flask-pymongo/

from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
import bson.json_util as json_util

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
    try:
        todo_many = db.todos.insert_many([
            {'title': "todo title one ", 'body': "todo body one "},
            {'title': "todo title two", 'body': "todo body two"},
            {'title': "todo title three", 'body': "todo body three"},
            {'title': "todo title four", 'body': "todo body four"},
            {'title': "todo title five", 'body': "todo body five"},
            {'title': "todo title six", 'body': "todo body six"},
        ], ordered=False)
    except Exception as e:
        return jsonify(message="duplicates encountered and ignored")

    return jsonify(message="success", insertedIds=todo_many.inserted_ids)

@app.route("/")
def home():
    todos = db.todos.find()
    return json_util.dumps([todo for todo in todos])

@app.route("/get_todo/<string:todoId>")
def insert_one(todoId):
    todo = db.todos.find_one({"_id": todoId})
    return json_util.dumps(message=todo)

@app.route("/replace_todo/<string:todoId>")
def replace_one(todoId):
    result = db.todos.replace_one({'_id': todoId}, {'title': "modified title"})
    return json_util.dumps({'id': result.raw_result})

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