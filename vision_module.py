import streamlit as st
from google import genai
from PIL import Image
import json
import os

# =======================
# 🔐 GEMINI API
# =======================
API_KEY = st.secrets["GEMINI_API_KEY"]  # or "YOUR_KEY_HERE"
client = genai.Client(api_key=API_KEY)

MODEL_ID = "gemini-2.5-flash"

# =======================
# 📁 INGREDIENTS JSON
# =======================
INGREDIENTS_FILE = "ingredients.json"

def load_ingredients():
    if os.path.exists(INGREDIENTS_FILE):
        with open(INGREDIENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"fridge_scans": []}

def save_ingredients(data):
    with open(INGREDIENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return True

# =======================
# 🎯 STREAMLIT UI
# =======================
st.title("📸 Smart Fridge Scanner (Gemini 1.5 Flash)")
st.write("Real-time ingredient recognition and similarity classification")

input_mode = st.radio("Choose input method:", ["Camera", "Upload"])

if input_mode == "Camera":
    image_source = st.camera_input("📷 Capture fridge / ingredient image")
else:
    image_source = st.file_uploader("📁 Upload fridge image", type=["jpg", "jpeg", "png"])

if image_source:
    image = Image.open(image_source)
    st.image(image, caption="🖼️ Image Preview", use_column_width=True)

    if st.button("🔍 Identify Ingredients"):
        st.info("Analyzing with Gemini... Please wait...")

        prompt = """
You are a food ingredient recognition expert AI.

🧊 Task:
Analyze this image and list all visible ingredients.

🔎 Important:
- If labels are visible, read them (e.g. 'Unsweetened Almond Milk', 'Greek Yogurt 2%')
- Distinguish similar items like "milk vs almond milk vs oat milk vs coconut milk"
- When unsure, set "confidence" to "low" and "specific_type" to "unknown"

📌 Output STRICT JSON ONLY in this format:

{
  "identified_items": [
    {
      "item_name": "string",
      "category": "vegetable | fruit | dairy | meat | pantry | beverage | grain | spice | frozen | unknown",
      "specific_type": "string or unknown",
      "confidence": "high | medium | low",
      "label_text_detected": "string or null"
    }
  ],
  "notes": "1-line summary of detection confidence"
}
"""

        response = client.models.generate_content(
            model=MODEL_ID,
            contents=[prompt, image]
        )

        try:
            cleaned = response.text.replace("```json","").replace("```","").strip()
            parsed = json.loads(cleaned)

            st.success("🎉 Ingredients Identified")
            st.json(parsed)

            # Save into ingredients.json
            data = load_ingredients()
            data["fridge_scans"].append(parsed)
            save_ingredients(data)

            st.success("📁 Saved to ingredients.json")
            st.write("📌 Your running ingredient history:")
            st.json(data)

        except Exception as e:
            st.error("❌ JSON Parsing Failed")
            st.code(response.text)
            st.exception(e)
