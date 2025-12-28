import os
import firebase_admin
from firebase_admin import credentials, firestore
from openai import OpenAI

# ================================
# 🔥 FIREBASE INITIALIZATION
# ================================
cred = credentials.Certificate("serviceAccountKey.json")
try:
    firebase_admin.initialize_app(cred)
except Exception:
    pass  # Ignore if already initialized

db = firestore.client()

# ================================
# ⚙️ OPENAI CLIENT INITIALIZATION
# ================================
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ================================
# 🔄 UNIT CONVERSION HELPERS
# ================================
CONVERSION_TABLE = {
    "flour": {"1 cup": "120 grams"},
    "sugar": {"1 cup": "200 grams"},
    "rice": {"1 cup": "185 grams"},
    "water": {"1 cup": "240 ml"},
    "milk": {"1 cup": "240 ml"},
    "oil": {"1 tbsp": "15 ml"},
    "butter": {"1 tbsp": "14 grams"},
}

def convert_measurement(ingredient, value, unit):
    """
    Try to estimate a conversion if known. Returns human-friendly string.
    """
    ingredient = ingredient.lower().strip()
    if ingredient in CONVERSION_TABLE:
        known = list(CONVERSION_TABLE[ingredient].items())[0]
        return f"Known conversion: {known[0]} ≈ {known[1]}"
    return "No exact conversion found. Ask the assistant for advice."


# ================================
# 📌 FETCH RECIPE CONTEXT
# ================================
def get_recipe_from_firebase(recipe_name):
    """
    Fetch a recipe document from Firestore.
    Firestore format recommended:
    collection: recipes
      document: "paneer gravy"
         fields:
            name: "Paneer Gravy"
            ingredients: ["paneer", "onion", "tomato", "ghee"]
            instructions: "Fry onions, add tomatoes..."
    """
    doc_ref = db.collection("recipes").where("name", "==", recipe_name).limit(1).stream()
    for doc in doc_ref:
        return doc.to_dict()
    return None


# ================================
# 🤖 CHATBOT ANSWER ENGINE
# ================================
def answer_query(recipe_name, user_question):
    recipe = get_recipe_from_firebase(recipe_name)

    if not recipe:
        return f"⚠️ Recipe '{recipe_name}' not found in database."

    ingredients = ", ".join(recipe.get("ingredients", []))
    instructions = recipe.get("instructions", "No instructions found.")

    system_prompt = f"""
You are a kitchen assistant. DO NOT invent recipes.
Context Recipe: {recipe_name}
Ingredients: {ingredients}
Instructions: {instructions}

Your tasks:
- Answer doubts about **measurements**, **ingredient substitution**, **cooking steps**, **units**
- DO NOT create a new recipe
- DO NOT hallucinate ingredients that are not listed
- If unsure, say: "I am not sure, please verify manually."
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",  # or gpt-5 if available
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ],
        temperature=0.4
    )

    return response.choices[0].message.content.strip()


# ================================
# 🧪 MAIN TEST HARNESS
# ================================
if __name__ == "__main__":
    print("=== Kitchen Assistant Ready ===")
    recipe_name = input("Enter recipe name: ")
    print("Ask any cooking question (type 'exit' to quit)\n")

    while True:
        q = input("❓ You: ")
        if q.lower() == "exit":
            break

        # Optional: try auto-conversion if user mentions grams/cups
        if "gram" in q.lower() or "cup" in q.lower():
            print("📏 Conversion hint:")
            # naive extraction
            words = q.lower().split()
            for w in words:
                if w.isalpha():  # assume ingredient word
                    print(convert_measurement(w, None, None))
                    break

        answer = answer_query(recipe_name, q)
        print("\n🤖 Assistant:", answer, "\n")
