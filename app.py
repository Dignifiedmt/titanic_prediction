"""Flask web application for the Titanic Survival Predictor."""
from pathlib import Path
import json
import math
import pickle

import pandas as pd
from flask import Flask, render_template, request

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "titanic_model.pkl"
DATA_PATH = BASE_DIR / "Titanic-Dataset.csv"
METADATA_PATH = BASE_DIR / "model_metadata.json"
FEATURES = ["Pclass", "Sex", "Age", "SibSp", "Parch", "Fare", "Embarked"]

app = Flask(__name__)

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Trained model not found at {MODEL_PATH}. "
        "Open Titanic_Model.ipynb and run all 10 steps first."
    )

# Pickle can execute code while loading. Only load a model file you created
# yourself or obtained from a trusted source. Keep training/deployment
# Python and scikit-learn versions compatible.
with MODEL_PATH.open("rb") as model_file:
    model = pickle.load(model_file)


def load_metadata():
    try:
        return json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def build_survival_chart():
    """Return observed survival rates by class and sex from the bundled CSV."""
    try:
        data = pd.read_csv(DATA_PATH)
        required = {"Pclass", "Sex", "Survived"}
        if not required.issubset(data.columns):
            return []
        data = data[list(required)].copy()
        data["Pclass"] = pd.to_numeric(data["Pclass"], errors="coerce")
        data["Survived"] = pd.to_numeric(data["Survived"], errors="coerce")
        data = data.dropna(subset=["Pclass", "Sex", "Survived"])
        grouped = data.groupby(["Pclass", "Sex"])["Survived"].agg(["mean", "count"])
        return [
            {"class": int(pclass), "sex": str(sex), "rate": round(float(row["mean"]) * 100, 1), "count": int(row["count"])}
            for (pclass, sex), row in grouped.iterrows()
        ]
    except (OSError, ValueError, KeyError, pd.errors.ParserError):
        return []


SURVIVAL_CHART = build_survival_chart()
MODEL_METADATA = load_metadata()


def render_home(*, error=None, result=None, values=None, status=200):
    return render_template(
        "index.html",
        error=error,
        result=result,
        values=values or {},
        survival_chart=SURVIVAL_CHART,
        metrics=MODEL_METADATA.get("test_metrics", {}),
    ), status


@app.get("/")
def home():
    return render_home()


@app.post("/predict")
def predict():
    values = request.form.to_dict()

    try:
        pclass = int(values.get("pclass", ""))
        sex = values.get("sex", "")
        age = float(values.get("age", ""))
        sibsp = int(values.get("sibsp", ""))
        parch = int(values.get("parch", ""))
        fare = float(values.get("fare", ""))
        embarked = values.get("embarked", "")

        if pclass not in (1, 2, 3):
            raise ValueError("Choose a valid passenger class.")
        if sex not in ("female", "male"):
            raise ValueError("Choose a valid sex option.")
        if not math.isfinite(age) or not 0 <= age <= 100:
            raise ValueError("Age must be a number between 0 and 100.")
        if not math.isfinite(fare) or not 0 <= fare <= 100000:
            raise ValueError("Enter a valid non-negative ticket fare.")
        if not 0 <= sibsp <= 20 or not 0 <= parch <= 20:
            raise ValueError("Family counts must be between 0 and 20.")
        if embarked not in ("S", "C", "Q"):
            raise ValueError("Choose a valid port of embarkation.")

        passenger = pd.DataFrame([{
            "Pclass": pclass, "Sex": sex, "Age": age, "SibSp": sibsp,
            "Parch": parch, "Fare": fare, "Embarked": embarked,
        }], columns=FEATURES)

        probabilities = model.predict_proba(passenger)[0]
        classes = list(model.classes_)
        survival_index = classes.index(1) if 1 in classes else classes.index(True)
        probability = float(probabilities[survival_index])
        prediction = int(model.predict(passenger)[0])
        family_size = sibsp + parch + 1
        result = {
            "label": "Survived" if prediction == 1 else "Did not survive",
            "class_name": "survived" if prediction == 1 else "not-survived",
            "probability": round(probability * 100, 1),
            "prediction": prediction,
            "not_survived_probability": round((1 - probability) * 100, 1),
            "family_size": family_size,
            "profile_note": (
                "Travelling with family" if family_size > 1 else "Travelling alone"
            ),
            "age_group": "Child" if age < 16 else "Adult",
        }
        return render_home(result=result, values=values)

    except (ValueError, TypeError, KeyError, IndexError) as exc:
        message = str(exc) or "Please check the passenger details and try again."
        return render_home(error=message, values=values, status=400)


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": True}


@app.get("/api/analytics")
def analytics():
    """Expose the same source data used by the on-page chart."""
    return {"survival_by_class_and_sex": SURVIVAL_CHART}


@app.errorhandler(404)
def page_not_found(_error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    # Debug is convenient locally. Turn it off for public deployment.
    app.run(host="127.0.0.1", port=5000, debug=True)
