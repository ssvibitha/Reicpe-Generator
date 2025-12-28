import json
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
try:
    firebase_admin.initialize_app(cred)
except:
    pass

db = firestore.client()

def load_patient_profile():
    with open("master_health_ingredients.json") as f:
        return json.load(f)

def recommend_recipes():
    data = load_patient_profile()
    patient = data["medical_profile"]

    query = db.collection("recipes")

    # FILTER RULES
    if patient["diabetes"]["status"] == "YES":
        query = query.where("dietary_profile.diabetic_safe", "==", True)

    if patient["renal_condition"]["status"] == "YES":
        query = query.where("dietary_profile.renal_safe", "==", True)

    if patient["allergies"]:
        for allergy in patient["allergies"]:
            query = query.where("ingredients", "not-in", [allergy])

    results = query.stream()
    return [doc.to_dict()["name"] for doc in results]


if __name__ == "__main__":
    print("🤖 Recommended recipes:")
    print(recommend_recipes())
