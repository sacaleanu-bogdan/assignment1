from flask import Flask, jsonify, abort, request
from flask_cors import CORS
from functools import wraps
from os import environ as env
from dotenv import load_dotenv
from jose import jwt # For JWT validation
from urllib.request import urlopen # For fetching Auth0 public keys
import json

load_dotenv()
AUTH0_DOMAIN = env.get("AUTH0_DOMAIN")
API_AUDIENCE = env.get("API_AUDIENCE")
ALGORITHMS = ["RS256"]

app=Flask(__name__)
CORS(app)

ITEMS_DATA = [
    {"id": 101, "name": "Pen", "owner_id": "user_a"},
    {"id": 102, "name": "Notebook", "owner_id": "user_a"},
    {"id": 201, "name": "Keyboard", "owner_id": "user_b"},
    {"id": 202, "name": "Mouse", "owner_id": "user_b"},
    {"id": 301, "name": "Monitor", "owner_id": "user_c"},
]

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", None)
        if not auth_header:
            abort(401, description="Authorization header is missing or empty.")

        parts = auth_header.split()
        if parts[0].lower() != "bearer":
            abort(401, description="Authorization header must start with Bearer.")
        elif len(parts) != 2:
            abort(401, description="Token format must be 'Bearer <token>'.")

        token = parts[1]
        try:
            jsonurl = urlopen(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")
            jwks = json.loads(jsonurl.read())

            payload = jwt.decode(
                token,
                jwks,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer=f"https://{AUTH0_DOMAIN}/"
            )
        except jwt.ExpiredSignatureError:
            abort(401, description="Token is expired.")
        except jwt.JWTClaimsError:
            abort(401, description="Invalid claims (check audience/issuer).")
        except Exception:
            abort(401, description="Invalid token or signature.")

        return f(*args, **kwargs)
    return decorated


@app.route('/api/items/<string:user_id>', methods=['GET'])
@requires_auth # Protected
def get_user_items(user_id):
    user_items=[item for item in ITEMS_DATA if item['owner_id']==user_id]
    if not user_items:
        abort(404, f'No items found for user id:{user_id}')
    return jsonify(user_items)

@app.route ('/api/items/users', methods=['GET'])
@requires_auth # Protected
def get_all_users():
    return jsonify(ITEMS_DATA)

@app.route('/api/items', methods=['POST'])
@requires_auth # Protected
def add_new_item():
    if not request.is_json:
        abort(400, 'Missing JSON in request')
    new_item=request.get_json()
    required_keys=['id', 'name', 'owner_id']

    if not all(key in new_item for key in required_keys):
        abort(400, 'Missing required fields: id, name , owner_id')

    ITEMS_DATA.append(new_item)
    return jsonify({
        "message": "Item added successffuly",
        "item" : new_item
    }), 201


if __name__=='__main__':
    from urllib.request import urlopen 
    app.run(debug=True, host='127.0.0.1', port=5000)