import pandas as pd
import json

# Load CSV
df = pd.read_csv("data/indian_food.csv")

# Function to clean text
def clean_text(x):
    return str(x).replace("\n", " ").strip()

recipes = []
for _, row in df.iterrows():
    recipe = {
        "name": clean_text(row.get("name", "")),
        "cuisine": "Indian",  # all from this dataset
        "ingredients": clean_text(row.get("ingredients", "")).split(", "),
        "course": clean_text(row.get("course", "")),
        "diet": clean_text(row.get("diet", "")),  # veg/non-veg
        "prep_time": row.get("prep_time", None),
        "cook_time": row.get("cook_time", None),
        "instructions": clean_text(row.get("instructions", "")),
        "nutrition": {
            "calories": row.get("calories", None),
            "protein_g": row.get("protein_g", None),
            "fat_g": row.get("fat_g", None),
            "carbs_g": row.get("carbs_g", None)
        }
    }
    recipes.append(recipe)

# Save as JSON
with open("data/processed_recipes.json", "w") as f:
    json.dump(recipes, f, indent=4)

print(f"✅ Processed {len(recipes)} recipes to JSON: data/processed_recipes.json")
