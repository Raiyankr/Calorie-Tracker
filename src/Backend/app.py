from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from datetime import date
import base64, os, json, requests, traceback
from openai import OpenAI


app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
app.config["JWT_SECRET_KEY"] = "1122334455"  # Change this in prod
jwt = JWTManager(app)

BASE_DIR = os.path.dirname(__file__)


# OLLAMA_API_URL = "http://localhost:11434/api/generate"

# MACRO_DATA_FILE = "app/calorie-tracker/src/Backend/macros.json"
# MACRO_HISTORY_DATA_FILE = "app/calorie-tracker/src/Backend/macrosHistory.json"



MACRO_DATA_FILE = os.path.join(BASE_DIR, 'macros.json')
MACRO_HISTORY_DATA_FILE = os.path.join(BASE_DIR, 'macrosHistory.json')
USERS_FILE = os.path.join(BASE_DIR, 'users.json')
# USERS_FILE = "app/calorie-tracker/src/Backend/users.json"

# -----------------------------------------------
# Helper Functions
# -----------------------------------------------
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE) as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def safe_load_json(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def safe_write_json(path, content):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'w') as f:
            json.dump(content, f, indent=2)
    except json.JSONDecodeError:
        return {}
# -----------------------------------------------
# User Authentication API
# -----------------------------------------------

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    users = load_users()

    if len(email) == 0:
        return jsonify({"error": "Enter Email"}), 410
    if len(password) == 0:
        return jsonify({"error": "Enter Password"}), 411

    elif email in users:
        return jsonify({"error": "User already exists"}), 400

    users[email] = generate_password_hash(password)
    save_users(users)

    return jsonify({"msg": "User registered successfully"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    users = load_users()

    if len(email) == 0:
        return jsonify({"error": "Enter Email"}), 410

    if email not in users or not check_password_hash(users[email], password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity=email)
    return jsonify(access_token=token)

# -----------------------------------------------
# User Macro data API
# -----------------------------------------------

# GET API CALL - retrieve the Macro data
@app.route('/api/last-macros', methods=['GET'])
@jwt_required()
def get_saved_macros():
    current_user = get_jwt_identity()

    if os.path.exists(MACRO_DATA_FILE):
        all_users_saved_data = safe_load_json(MACRO_DATA_FILE)

        if current_user not in all_users_saved_data:
            return jsonify({"error": "No macro data for this user"}), 404    

        return jsonify(all_users_saved_data[current_user])
    
    else:
        return jsonify({"error": "No saved macro data found"}), 404

@app.route('/api/user-history', methods=['GET'])
@jwt_required()
def get_user_history():
    current_user = get_jwt_identity()

    if os.path.exists(MACRO_HISTORY_DATA_FILE):
        all_users_history = safe_load_json(MACRO_HISTORY_DATA_FILE)
        all_user_macro = safe_load_json(MACRO_DATA_FILE)
        
        if current_user not in all_users_history and current_user not in all_user_macro:
            return jsonify([{"date" : str(date.today()),
                "calorie": 0,
                "protein": 0,
                "carbs": 0,
                "fat": 0}])
        elif current_user not in all_users_history:
            return jsonify([all_user_macro[current_user]])
        
        resultHistory = all_users_history[current_user]
        resultHistory.append(all_user_macro[current_user])

        if len(resultHistory) > 7:
            return jsonify(resultHistory[-7:])

        return jsonify(resultHistory)
    
    else:
        return jsonify({"error": "No saved macro data found"}), 404
    
# GET API CALL - Reset the Macro data and return it
@app.route('/api/reset-macros', methods=['GET'])
@jwt_required()
def reset_saved_macros():
    current_user = get_jwt_identity()

    if os.path.exists(MACRO_DATA_FILE):
        resetData = {'date': str(date.today()), 'calorie': 0, 'protein': 0, 'carbs': 0, 'fat': 0}

        all_users_saved_data = safe_load_json(MACRO_DATA_FILE)
        all_users_saved_data[current_user] = resetData
        
        safe_write_json(MACRO_DATA_FILE, all_users_saved_data)
        
        return resetData
    else:
        return jsonify({"error": "No saved macro data found"}), 404
    
# POST API CALL - To call ollama in the backend
@app.route('/api/generate', methods=['POST'])
@jwt_required()
def generate():
    current_user = get_jwt_identity()
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    image_file = request.files['image']
    image_bytes = image_file.read()
    encoded_image = base64.b64encode(image_bytes).decode('utf-8')
    client = OpenAI(api_key="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")

    print("GETTING IMAGE")

    prompt = (
        "Analyze this picture and tell me the macros of it "
        "(Calorie, Protein, Carbs, Fats). If you don't know the exact then guess. "
        "I want you to give me one number for each metric as your best guess. "
        "Don't explain anything—just give me the values for (Calorie, Protein, Carbs, Fats) in one lines."
        "Only give me the values (no need to mention units or put commas)."
        "Just tell me the values. "
    )

    # response = requests.post(OLLAMA_API_URL, json={
    #     "model": "gemma3:4b",
    #     "prompt": prompt,
    #     "images": [encoded_image],
    #     "stream": False
    # })
    response = client.responses.create(
    model="gpt-4.1",
    input=[
            {
                "role": "user",
                "content": [
                    { "type": "input_text", "text": prompt},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{encoded_image}",
                    },
                ],
            }
        ],
    )
    data = response.output_text
    lines = data.split()
    if len(lines) < 4:
        return jsonify({"error": "Incomplete response"}), 500

    try:
        calorie = float(lines[0])
        protein = float(lines[1])
        carbs = float(lines[2])
        fat = float(lines[3])
        currentDate = str(date.today())

        macro_data = {
            "calorie": calorie,
            "protein": protein,
            "carbs": carbs,
            "fat": fat
        }

        all_users_saved_data = safe_load_json(MACRO_DATA_FILE)

        if current_user not in all_users_saved_data:
            all_users_saved_data[current_user] = {
                "date" : currentDate,
                "calorie": 0,
                "protein": 0,
                "carbs": 0,
                "fat": 0
            }

        current_user_saved_data = all_users_saved_data[current_user]

        if current_user_saved_data['date'] == currentDate:
            newData = {
                "date" : currentDate,
                "calorie": current_user_saved_data['calorie'] + macro_data['calorie'],
                "protein": current_user_saved_data['protein'] + macro_data['protein'],
                "carbs": current_user_saved_data['carbs'] + macro_data['carbs'],
                "fat": current_user_saved_data['fat'] + macro_data['fat']
            }
        else:
            # Add old data to history
            all_users_history = safe_load_json(MACRO_HISTORY_DATA_FILE)

            if current_user not in all_users_history:
                all_users_history[current_user] = []

            current_user_history = all_users_history[current_user]
            current_user_history.append(current_user_saved_data)

            all_users_history[current_user] = current_user_history

            safe_write_json(MACRO_HISTORY_DATA_FILE, all_users_history)

            newData = {
                "date" : currentDate,
                "calorie": macro_data['calorie'],
                "protein": macro_data['protein'],
                "carbs": macro_data['carbs'],
                "fat": macro_data['fat']
            }

        all_users_saved_data[current_user] = newData
        safe_write_json(MACRO_DATA_FILE, all_users_saved_data)

        return jsonify(newData)
    
    except Exception as e:
        traceback.print_exc()  # Show full stack trace
        return jsonify({"error": f"Server error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(port=5050, debug=True)








