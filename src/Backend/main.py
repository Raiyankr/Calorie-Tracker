from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from datetime import date
import base64, os, traceback
from openai import OpenAI
from dotenv import load_dotenv
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base, User, Macro, MacroHistory

load_dotenv()

# Database setup
engine = create_engine(os.getenv("DATABASE_URL"))
SessionLocal = scoped_session(sessionmaker(bind=engine))
Base.metadata.create_all(engine)

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "http://localhost:50500", "https://calorie-tracker-sage.vercel.app"]}})
app.config["JWT_SECRET_KEY"] = "1122334455"
jwt = JWTManager(app)

# -----------------------------
# User Authentication
# -----------------------------
@app.route('/api/register', methods=['POST'])
def register():
    session = SessionLocal()
    try:
        data = request.json
        email = data.get("email")
        password = data.get("password")
        calorie = data.get("calorie")
        protein = data.get("protein")
        carbs = data.get("carbs")
        fat = data.get("fat")

        if not email:
            return jsonify({"error": "Enter Email"}), 410
        if not password:
            return jsonify({"error": "Enter Password"}), 411

        if not calorie or not protein or not carbs or not fat:
            return jsonify({"error": "Enter Information"}), 412

        if session.query(User).filter_by(email=email).first():
            return jsonify({"error": "User already exists"}), 400

        hashed_password = generate_password_hash(password)
        user = User(email=email, password=hashed_password, targetCalorie=calorie, targetProtein=protein, targetCarbs=carbs, targetFat=fat)
        session.add(user)
        session.commit()
        return jsonify({"msg": "User registered successfully"}), 201
    finally:
        session.close()


@app.route('/api/login', methods=['POST'])
def login():
    session = SessionLocal()
    try:
        data = request.json
        email = data.get("email")
        password = data.get("password")
        user = session.query(User).filter_by(email=email).first()

        if not email:
            return jsonify({"error": "Enter Email"}), 410
        if not user or not check_password_hash(user.password, password):
            return jsonify({"error": "Invalid credentials"}), 401

        token = create_access_token(identity=email)
        return jsonify(access_token=token)
    finally:
        session.close()


# -----------------------------
# Macro Endpoints
# -----------------------------
@app.route('/api/last-macros', methods=['GET'])
@jwt_required()
def get_saved_macros():
    session = SessionLocal()
    try:
        email = get_jwt_identity()
        user = session.query(User).filter_by(email=email).first()
        macro = session.query(Macro).filter_by(user_id=user.id).first()

        print("Getting User Info")

        if not macro:
            return jsonify({
                "date": str(date.today()),
                "calorie": 0,
                "protein": 0,
                "carbs": 0,
                "fat": 0,
                "targetCalorie": user.targetCalorie,
                "targetProtein": user.targetProtein,
                "targetCarbs": user.targetCarbs,
                "targetFat": user.targetFat
            })
        return jsonify({
            "date": str(macro.date),
            "calorie": macro.calorie,
            "protein": macro.protein,
            "carbs": macro.carbs,
            "fat": macro.fat,
            "TargetCalorie": user.targetCalorie,
            "TargetProtein": user.targetProtein,
            "TargetCarbs": user.targetCarbs,
            "TargetFat": user.targetFat
        })
    finally:
        session.close()


@app.route('/api/user-history', methods=['GET'])
@jwt_required()
def get_user_history():
    session = SessionLocal()
    try:
        email = get_jwt_identity()
        user = session.query(User).filter_by(email=email).first()

        history = session.query(MacroHistory).filter_by(user_id=user.id).order_by(MacroHistory.date).all()
        macro_today = session.query(Macro).filter_by(user_id=user.id).first()

        history_data = [
            {"date": str(entry.date), "calorie": entry.calorie, "protein": entry.protein,
             "carbs": entry.carbs, "fat": entry.fat}
            for entry in history
        ]
        if macro_today:
            history_data.append({
                "date": str(macro_today.date), "calorie": macro_today.calorie,
                "protein": macro_today.protein, "carbs": macro_today.carbs, "fat": macro_today.fat
            })

        return jsonify(history_data[-7:] if len(history_data) > 7 else history_data)
    finally:
        session.close()


@app.route('/api/reset-macros', methods=['GET'])
@jwt_required()
def reset_saved_macros():
    session = SessionLocal()
    try:
        today = date.today()
        email = get_jwt_identity()
        user = session.query(User).filter_by(email=email).first()
        macro = session.query(Macro).filter_by(user_id=user.id).first()

        if macro:
            history_entry = MacroHistory(
                user_id=user.id,
                date=macro.date,
                calorie=macro.calorie,
                protein=macro.protein,
                carbs=macro.carbs,
                fat=macro.fat
            )
            session.add(history_entry)

            macro.date = today
            macro.calorie = 0
            macro.protein = 0
            macro.carbs = 0
            macro.fat = 0
        else:
            macro = Macro(user_id=user.id, date=today, calorie=0, protein=0, carbs=0, fat=0)
            session.add(macro)

        session.commit()
        return jsonify({"date": str(today), "calorie": 0, "protein": 0, "carbs": 0, "fat": 0})
    finally:
        session.close()


@app.route('/api/generate', methods=['POST'])
@jwt_required()
def generate():
    session = SessionLocal()
    try:
        email = get_jwt_identity()
        user = session.query(User).filter_by(email=email).first()
        if 'image' not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        image_file = request.files['image']
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

        prompt = (
            "Analyze this picture and tell me the macros of it "
            "(Calorie, Protein, Carbs, Fats). If you don't know the exact then guess. "
            "I want you to give me one number for each metric as your best guess. "
            "Don't explain anything—just give me the values for (Calorie, Protein, Carbs, Fats) in one lines. "
            "Only give me the values (no units, no commas)."
        )

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

        calorie = float(lines[0])
        protein = float(lines[1])
        carbs = float(lines[2])
        fat = float(lines[3])
        currentDate = date.today()

        macro = session.query(Macro).filter_by(user_id=user.id).first()

        if macro and macro.date == currentDate:
            macro.calorie += calorie
            macro.protein += protein
            macro.carbs += carbs
            macro.fat += fat
        else:
            if macro:
                history_entry = MacroHistory(
                    user_id=user.id,
                    date=macro.date,
                    calorie=macro.calorie,
                    protein=macro.protein,
                    carbs=macro.carbs,
                    fat=macro.fat
                )
                session.add(history_entry)

                macro.date = currentDate
                macro.calorie = calorie
                macro.protein = protein
                macro.carbs = carbs
                macro.fat = fat
            else:
                new_macro = Macro(user_id=user.id, date=currentDate, calorie=calorie, protein=protein, carbs=carbs, fat=fat)
                session.add(new_macro)

        session.commit()
        return jsonify({
            "date": str(currentDate), "calorie": calorie, "protein": protein, "carbs": carbs, "fat": fat
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Server error: {str(e)}"}), 500
    finally:
        session.close()


if __name__ == '__main__':
    app.run(port=5050, debug=True)
