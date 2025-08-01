import json
import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Macro, MacroHistory

load_dotenv()

# Connect to Neon database
engine = create_engine(os.getenv("DATABASE_URL"))
Session = sessionmaker(bind=engine)
session = Session()

# Load your JSON file
with open("data.json") as f:
    data = json.load(f)

# Example structure assumed:
# {
#   "users": {
#     "user@example.com": {
#       "password": "hashed_password",
#       "macros": {
#         "date": "2024-07-30",
#         "calorie": 500,
#         "protein": 40,
#         "carbs": 50,
#         "fat": 20
#       },
#       "history": [
#         { "date": "2024-07-29", "calorie": 450, "protein": 30, "carbs": 45, "fat": 15 },
#         ...
#       ]
#     }
#   }
# }

for email, info in data["users"].items():
    user = User(email=email, password=info["password"])
    session.add(user)
    session.flush()  # Ensures user.id is available

    # Add current macro
    if "macros" in info:
        m = info["macros"]
        macro = Macro(
            user_id=user.id,
            date=datetime.strptime(m["date"], "%Y-%m-%d").date(),
            calorie=m["calorie"],
            protein=m["protein"],
            carbs=m["carbs"],
            fat=m["fat"]
        )
        session.add(macro)

    # Add macro history
    for h in info.get("history", []):
        history = MacroHistory(
            user_id=user.id,
            date=datetime.strptime(h["date"], "%Y-%m-%d").date(),
            calorie=h["calorie"],
            protein=h["protein"],
            carbs=h["carbs"],
            fat=h["fat"]
        )
        session.add(history)

session.commit()
session.close()
print("✅ Migration complete.")