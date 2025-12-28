import requests
from constraint_engine import filter_ingredients

# Replace with your Spoonacular API key
API_KEY = "YOUR_SPOONACULAR_KEY"
BASE_URL = "https://api.spoonacular.com/recipes/complexSearch"

# Map patient conditions to API parameters
CONDITION_TO_API = {
    "diabetes": {"maxSugar": 5, "diet": "low-glycemic"},
    "gerd": {"excludeIngredients": "tomato,spicy,citrus,coffee"},
    "anxiety": {"excludeIngredients": "caffeine"}
}

def build_api_params(master_file="master_health_ingredients.json"):
    safe, unsafe = filter_ingredients(master_file)
    params = {
        "apiKey": API_KEY,
        "includeIngredients": ",".join(safe),
        "excludeIngredients": ",".join([u["name"] for u in unsafe]),
        "number": 5
    }

    # Load patient conditions
    with open(master_file) as f:
        master = json.load(f)
    conditions = [c.lower() for c in master["medical_report"].get("conditions", [])]

    # Add API parameters based on conditions
    for cond in conditions:
        if cond in CONDITION_TO_API:
            params.update(CONDITION_TO_API[cond])
    return params

def fetch_recipes(master_file="master_health_ingredients.json"):
    params = build_api_params(master_file)
    response = requests.get(BASE_URL, params=params)
    if response.status_code != 200:
        return {"error": "API Error", "details": response.text}
    return response.json()

# Quick test
if __name__ == "__main__":
    recipes = fetch_recipes()
    print(recipes)
