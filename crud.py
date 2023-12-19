
from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient('mongodb://localhost:27017')
db = client.test

@app.route('/create', methods=['POST'])
def create():
    data = request.get_json()
    db.collection.insert_one(data)
    return jsonify({'message': 'Data created successfully'})

@app.route('/read', methods=['GET'])
def read():
    data = db.collection.find()
    return jsonify({'data': data})

@app.route('/update', methods=['PUT'])
def update():
    data = request.get_json()
    db.collection.update_one({'id': data['id']}, {'$set': data})
    return jsonify({'message': 'Data updated successfully'})

@app.route('/delete', methods=['DELETE'])
def delete():
    data = request.get_json()
    db.collection.delete_one({'id': data['id']})
    return jsonify({'message': 'Data deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True)
