"""Flask web application for the Titanic Survival Predictor."""
from pathlib import Path
import pickle

import pandas as pd
from flask import Flask, render_template, request

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "titanic_model.pkl"

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


def render_home(*, error=None, result=None, values=None, status=200):
    return render_template(
        "index.html",
        error=error,
        result=result,
        values=values or {},
    ), status


@app.get("/")
def home():
    return render_home()


@app.post("/predict")
def predict():
    values = request.form.to_dict()

    try:
        # Parse and validate the submitted values on the server.
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
        if not 0 <= age <= 100:
            raise ValueError("Age must be between 0 and 100.")
        if not 0 <= fare <= 100000:
            raise ValueError("Enter a valid non-negative ticket fare.")
        if not 0 <= sibsp <= 20 or not 0 <= parch <= 20:
            raise ValueError("Family counts must be between 0 and 20.")
        if embarked not in ("S", "C", "Q"):
            raise ValueError("Choose a valid port of embarkation.")

        passenger = pd.DataFrame([{
            "Pclass": pclass,
            "Sex": sex,
            "Age": age,
            "SibSp": sibsp,
            "Parch": parch,
            "Fare": fare,
            "Embarked": embarked,
        }], columns=FEATURES)

        prediction = int(model.predict(passenger)[0])
        probability = float(model.predict_proba(passenger)[0, 1])

        result = {
            "label": "Survived" if prediction == 1 else "Did not survive",
            "class_name": "survived" if prediction == 1 else "not-survived",
            "probability": round(probability * 100, 1),
            "prediction": prediction,
        }
        return render_home(result=result, values=values)

    except (ValueError, TypeError, KeyError) as exc:
        message = str(exc) or "Please check the passenger details and try again."
        return render_home(error=message, values=values, status=400)


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": True}


@app.errorhandler(404)
def page_not_found(_error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    # Debug is convenient locally. Turn it off for public deployment.
    app.run(host="127.0.0.1", port=5000, debug=True)
