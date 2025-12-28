import json

def load_master():
    with open("master_health_ingredients.json") as f:
        return json.load(f)

def filter_ingredients():
    data = load_master()
    
    safe = []
    unsafe = []

    for item in data["ingredients_profile"]["items"]:
        if item["is_safe_for_patient"]:
            safe.append(item["name"])
        else:
            unsafe.append({"name": item["name"], "reason": item["reason"]})

    return safe, unsafe

if __name__ == "__main__":
    safe, unsafe = filter_ingredients()
    print("🛡 SAFE INGREDIENTS:", safe)
    print("❌ BLOCKED:", unsafe)
