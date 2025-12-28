import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

recipes = [
    {
        "id": "paneer-butter-masala",
        "name": "Paneer Butter Masala",
        "cuisine": "Indian",
        "dietary_profile": {
            "gluten_free": True,
            "vegan": False,
            "diabetic_safe": False,
            "renal_safe": True
        },
        "ingredients": ["paneer", "butter", "tomato", "cream"],
        "instructions": "Fry onions, blend tomatoes, cook with paneer.",
        "nutrition": {
            "calories": 350,
            "sugar_g": 8,
            "sodium_mg": 320
        }
    },
    {
        "id": "moong-dal-khichdi",
        "name": "Moong Dal Khichdi",
        "cuisine": "Indian",
        "dietary_profile": {
            "gluten_free": True,
            "vegan": True,
            "diabetic_safe": True,
            "renal_safe": True
        },
        "ingredients": ["moong dal", "rice", "ghee", "salt"],
        "instructions": "Cook rice + dal, add tadka.",
        "nutrition": {
            "calories": 280,
            "sugar_g": 2,
            "sodium_mg": 180
        }
    },
]

for r in recipes:
    db.collection("recipes").document(r["id"]).set(r)

print("✔ Upload Complete!")
