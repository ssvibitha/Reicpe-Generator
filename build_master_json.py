import json
from datetime import datetime

# ==========================================================
# RULE ENGINE HELPERS
# ==========================================================

def analyze_item_safety(conditions, allergies, medications, item):
    name = item["name"].lower()
    reason_list = []
    safe = True

    # --- Condition Rules ---
    if "anxiety" in conditions and ("caffeine" in name or "coffee" in name):
        safe = False
        reason_list.append("Caffeine may trigger anxiety/palpitations")

    if "gerd" in conditions and ("spicy" in name or "acidic" in name or "tomato" in name or "coffee" in name):
        safe = False
        reason_list.append("GERD trigger food")

    # --- Allergy Rules ---
    for allergy in allergies:
        if allergy.lower() in name:
            safe = False
            reason_list.append(f"Allergy match: {allergy}")

    # --- Medication Interaction Rules ---
    for med in medications:
        med_lower = med.lower()

        # Grapefruit interactions (common w/ heart meds, anxiety meds)
        if "grapefruit" in name and ("statin" in med_lower or "benzodiazepine" in med_lower):
            safe = False
            reason_list.append("⚠ Grapefruit-medication interaction risk")

        # Caffeine interactions (anxiety / stimulants)
        if "caffeine" in name and ("lorazepam" in med_lower or "benzodiazepine" in med_lower):
            safe = False
            reason_list.append("⚠ Avoid caffeine while on benzodiazepines")

    # Clean output
    reason = "; ".join(reason_list) if reason_list else "Safe to use"
    return safe, reason


def expiry_status(expiry_date_str):
    """Check expiry status & urgency labels"""
    if not expiry_date_str:
        return "unknown"

    try:
        exp = datetime.strptime(expiry_date_str, "%Y-%m-%d")
        days = (exp - datetime.now()).days

        if days < 0:
            return f"expired ({abs(days)} days ago)"
        elif days <= 3:
            return "expiring soon"
        elif days <= 7:
            return "use this week"
        else:
            return "fresh"
    except:
        return "invalid date"


def daily_meal_recommendations(conditions, ingredients):
    recs = []

    # GERD-friendly suggestions
    if "gerd" in conditions:
        recs.append("Focus meals: oatmeal, bananas, lean meats, rice, and non-citrus fruits")
        recs.append("Avoid tomato sauces, spicy curries, citrus juices, coffee")

    # Anxiety-friendly
    if "anxiety" in conditions:
        recs.append("Choose calming foods: green leafy veggies, chamomile tea, nuts, berries")
        recs.append("Avoid heavy caffeine and energy drinks")

    # Ingredients-based triggers
    if any("milk" in i["name"].lower() for i in ingredients):
        recs.append("Consider lactose-free options if digestion issues occur")

    return recs or ["Maintain a balanced plate: veggies + lean protein + whole grains"]


# ==========================================================
# MAIN PIPELINE
# ==========================================================

# ----- Load Inputs -----
with open("medical_report.json") as f:
    medical_data = json.load(f)

with open("ingredients.json") as f:
    ingredients_data = json.load(f)

# ----- Extract Fields -----
conditions = [c.lower() for c in medical_data.get("conditions", [])]
allergies = medical_data.get("allergies", [])
medications = medical_data.get("medications", [])

# ==========================================================
# Build MASTER JSON
# ==========================================================

master = {
    "patient_profile": medical_data.get("patient_profile", {}),
    "medical_report": medical_data,
    
    "ingredients_profile": {
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "items": []
    },

    "compatibility_summary": {
        "safe_items": [],
        "risky_items": [],
        "avoid_items": [],
        "expiry_alerts": [],
        "medication_interaction_warnings": [],
        "notes": "Generated based on conditions + allergies + medications + food rules."
    },

    "nutrition_coach": {
        "daily_meal_recommendations": [],
        "foods_to_avoid_today": [],
        "safe_substitutes": []
    }
}


# ----- Process Ingredients -----
for item in ingredients_data.get("items", []):
    safe, reason = analyze_item_safety(conditions, allergies, medications, item)
    
    expiry_state = expiry_status(item.get("expiry_date", ""))

    item_record = {
        "name": item["name"],
        "category": item.get("category", ""),
        "quantity": item.get("quantity", ""),
        "expiry_date": item.get("expiry_date", ""),
        "expiry_status": expiry_state,
        "dietary_classification": item.get("dietary_classification", ""),
        "is_safe_for_patient": safe,
        "reason": reason
    }

    master["ingredients_profile"]["items"].append(item_record)

    # Classification summary
    if safe:
        master["compatibility_summary"]["safe_items"].append(item["name"])
    elif "allergy" in reason.lower():
        master["compatibility_summary"]["avoid_items"].append(item["name"])
    else:
        master["compatibility_summary"]["risky_items"].append(item["name"])

    # Expiry alerts
    if expiry_state in ["expired", "expiring soon"]:
        master["compatibility_summary"]["expiry_alerts"].append(f"{item['name']} - {expiry_state}")

    # Medication warnings
    if "⚠" in reason:
        master["compatibility_summary"]["medication_interaction_warnings"].append(
            f"{item['name']} - {reason}"
        )


# ----- Add Meal Recommendations -----
master["nutrition_coach"]["daily_meal_recommendations"] = daily_meal_recommendations(conditions, master["ingredients_profile"]["items"])

# Foods to avoid
master["nutrition_coach"]["foods_to_avoid_today"] = master["compatibility_summary"]["risky_items"] + master["compatibility_summary"]["avoid_items"]

# Safe substitutes (basic)
if "milk" in str(master["compatibility_summary"]["avoid_items"]).lower():
    master["nutrition_coach"]["safe_substitutes"].append("Try almond milk or lactose-free milk")


# ----- Save Output -----
with open("master_health_ingredients.json", "w") as f:
    json.dump(master, f, indent=4)

print("\n🎉 MASTER JSON CREATED SUCCESSFULLY!")
print("📌 Saved as: master_health_ingredients.json")
