import json
from google import genai

# Gemini API key
API_KEY = "YOUR_GEMINI_KEY"
MODEL = "gemini-1.5-pro"
client = genai.Client(api_key=API_KEY)

def refine_recipes(master_file="master_health_ingredients.json", recipes=None):
    with open(master_file) as f:
        master = json.load(f)

    safe, unsafe = [], []
    for item in master["ingredients_profile"]["items"]:
        if item.get("is_safe_for_patient"):
            safe.append(item["name"])
        else:
            unsafe.append(item["name"])

    # Build the multi-step prompt
    prompt = f"""
You are a professional nutritionist AI.

Patient profile:
{json.dumps(master['patient_profile'], indent=2)}

Patient Conditions:
{json.dumps(master['medical_report'].get('conditions', []), indent=2)}

Safe Ingredients:
{json.dumps(safe, indent=2)}

Unsafe Ingredients:
{json.dumps(unsafe, indent=2)}

Raw API Recipes:
{json.dumps(recipes, indent=2)}

TASKS:
1. Remove any recipe containing unsafe ingredients.
2. For each safe recipe, output in JSON:
   - recipe_name
   - why_safe
   - medical_benefit
   - serving_advice
   - caution_note
3. STRICT JSON ONLY.
"""
    response = client.models.generate_content(
        model=MODEL,
        contents=[prompt],
        config={"temperature": 0.2}
    )

    # Clean and parse
    try:
        clean = response.text.strip()
        return json.loads(clean)
    except:
        return {"raw_output": response.text}

# Quick test
if __name__ == "__main__":
    from recipe_api import fetch_recipes
    api_results = fetch_recipes()
    refined = refine_recipes(recipes=api_results.get("results", []))
    print(json.dumps(refined, indent=2))
