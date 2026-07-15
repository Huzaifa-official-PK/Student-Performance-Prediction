# ==========================================================
# Student Performance Prediction System
# Flask Application
# Part 1
# ==========================================================

from pathlib import Path

import joblib
import pandas as pd

from flask import Flask, jsonify, render_template, request

# ==========================================================
# Flask App
# ==========================================================

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

# ==========================================================
# Load Model
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "model.pkl"

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        "Model not found! Run model.py first."
    )

model = joblib.load(MODEL_PATH)

REQUIRED_FIELDS = [
    "Hours_Studied",
    "Attendance",
    "Parental_Involvement",
    "Access_to_Resources",
    "Extracurricular_Activities",
    "Sleep_Hours",
    "Previous_Scores",
    "Motivation_Level",
    "Internet_Access",
    "Tutoring_Sessions",
    "Family_Income",
    "Teacher_Quality",
    "School_Type",
    "Peer_Influence",
    "Physical_Activity",
    "Learning_Disabilities",
    "Parental_Education_Level",
    "Distance_from_Home",
    "Gender"
]

NUMERIC_FIELDS = [
    "Hours_Studied",
    "Attendance",
    "Sleep_Hours",
    "Previous_Scores",
    "Tutoring_Sessions",
    "Physical_Activity"
]


def build_input_data(form_data):
    input_data = {}

    value_limits = {
        "Hours_Studied": (0, 24),
        "Attendance": (0, 100),
        "Sleep_Hours": (1, 24),
        "Previous_Scores": (0, 100),
        "Tutoring_Sessions": (0, 20),
        "Physical_Activity": (0, 24),
    }

    for field in NUMERIC_FIELDS:
        try:
            value = float(form_data[field])
        except (KeyError, TypeError, ValueError):
            raise ValueError(f"Invalid numeric value for {field}.")

        if not value.is_integer():
            raise ValueError(f"{field} must be a whole number.")

        value = int(value)

        min_value, max_value = value_limits[field]
        if not (min_value <= value <= max_value):
            raise ValueError(
                f"{field} must be between {min_value} and {max_value}."
            )

        input_data[field] = value

    for field in REQUIRED_FIELDS:
        if field not in NUMERIC_FIELDS:
            input_data[field] = form_data[field]

    return input_data


def get_grade_details(prediction):
    if prediction >= 90:
        return "A+", "Outstanding"
    if prediction >= 80:
        return "A", "Excellent"
    if prediction >= 70:
        return "B", "Very Good"
    if prediction >= 60:
        return "C", "Good"
    if prediction >= 50:
        return "D", "Average"
    return "F", "Needs Improvement"

print("=" * 60)
print("Model Loaded Successfully")
print("=" * 60)

# ==========================================================
# Home Page
# ==========================================================

@app.route("/")
def home():

    return render_template(

        "home.html",

        page="home"

    )

# ==========================================================
# Prediction Page
# ==========================================================

@app.route("/prediction")
def prediction():

    return render_template(

        "prediction.html",

        page="prediction"

    )

# ==========================================================
# About Page
# ==========================================================

@app.route("/about")
def about():

    return render_template(

        "about.html",

        page="about"

    )

# ==========================================================
# Prediction API
# ==========================================================

@app.route("/predict", methods=["POST"])
def predict():

    try:
        data = request.form

        missing_fields = [
            field for field in REQUIRED_FIELDS
            if data.get(field, "").strip() == ""
        ]

        if missing_fields:
            return jsonify({
                "success": False,
                "error": "Please fill all required fields."
            }), 400

        input_data = build_input_data(data)
        input_df = pd.DataFrame([input_data])

        prediction = float(model.predict(input_df)[0])
        prediction = min(100.0, max(0.0, prediction))
        prediction = round(prediction, 2)
        grade, performance = get_grade_details(prediction)

        return jsonify({
            "success": True,
            "predicted_score": prediction,
            "grade": grade,
            "performance": performance
        })

    except ValueError as exc:
        return jsonify({
            "success": False,
            "error": str(exc)
        }), 400

    except Exception:
        return jsonify({
            "success": False,
            "error": "Prediction failed. Please try again."
        }), 500


# ==========================================================
# Application Start
# ==========================================================

if __name__ == "__main__":

    app.run(

        debug=True,

        host="0.0.0.0",

        port=5000

    )