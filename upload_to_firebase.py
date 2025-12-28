from firebase_connect import db  # your firebase setup file
import json

# Load processed recipes
with open("data/processed_recipes.json") as f:
    recipes = json.load(f)

collection = db.collection("recipes")

for recipe in recipes[:500]:  # Limit for testing
    doc_id = recipe["name"].replace(" ", "_").lower()
    collection.document(doc_id).set(recipe)

print("✅ Recipes uploaded to Firebase Firestore!")
