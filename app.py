
# pip install Flask-PyMongo
# https://stackabuse.com/integrating-mongodb-with-flask-using-flask-pymongo/

from flask import Flask, render_template
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
mongo = PyMongo(app)
db = mongo.db

@app.route('/')
def home_page():
    mydict = { "name": "John", "address": "Highway 37" }

    x = db.todos.insert_one(mydict)
    print(x.inserted_id)

    for x in db.todos.find():
        print(x)

    return render_template('index.html', 
                            online_users=list(db.todos.find()))

@app.route("/user/<username>")
def user_profile(username):
    return render_template("user.html", 
                            user=username)

if __name__ == '__main__':
    app.run(debug=True)