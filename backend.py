from flask import Flask, jsonify, abort, request
from flask_cors import CORS
import requests
import json

app=Flask(__name__)
CORS(app)

ITEMS_DATA = [
    {"id": 101, "name": "Pen", "owner_id": "user_a"},
    {"id": 102, "name": "Notebook", "owner_id": "user_a"},
    {"id": 201, "name": "Keyboard", "owner_id": "user_b"},
    {"id": 202, "name": "Mouse", "owner_id": "user_b"},
    {"id": 301, "name": "Monitor", "owner_id": "user_c"},
]


@app.route('/api/items/<string:user_id>', methods=['GET'])
def get_user_items(user_id):
    user_items=[item for item in ITEMS_DATA if item['owner_id']==user_id]
    if not user_items:
        abort(404, 'No items found for user id:{user_id}')
    return jsonify(user_items)

@app.route ('/api/items/users', methods=['GET'])
def get_all_users():
    return jsonify(ITEMS_DATA)

@app.route('/api/items', methods=['POST'])
def add_new_item():
    if not request.is_json:
        abort(400, 'Missing JSON in request')
    new_item=request.get_json()
    required_keys=['id', 'name', 'owner_id']

    if not all(key in new_item for key in required_keys):
        abort(400, 'Missing required fields: id, name , owner_id')

    return jsonify({
        "message": "Item added successffuly",
        "item" : new_item
    }), 201


if __name__=='__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
