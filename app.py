import os
import pickle
import math
import pandas as pd

from flask import Flask, render_template, request

app = Flask(__name__)

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "titanic_model.pkl"
)

# Load the trained model
with open(MODEL_PATH, "rb") as file:
    model = pickle.load(file)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():

    try:
        # Collect form values
        pclass = int(request.form["pclass"])
        sex = request.form["sex"]
        age = float(request.form["age"])
        sibsp = int(request.form["sibsp"])
        parch = int(request.form["parch"])
        fare = float(request.form["fare"])
        embarked = request.form["embarked"]

        form_values = {
            "pclass": str(pclass),
            "sex": sex,
            "age": str(age),
            "sibsp": str(sibsp),
            "parch": str(parch),
            "fare": str(fare),
            "embarked": embarked,
        }

        # Validate numeric inputs
        if not all(math.isfinite(value) for value in (age, fare)):
            raise ValueError("Values must be finite.")

        if age < 0 or fare < 0 or sibsp < 0 or parch < 0:
            raise ValueError("Values cannot be negative.")

        if pclass not in [1, 2, 3]:
            raise ValueError("Invalid passenger class.")

        if sex not in ["male", "female"]:
            raise ValueError("Invalid sex selection.")

        if embarked not in ["S", "C", "Q"]:
            raise ValueError("Invalid embarkation port.")

        # Prepare passenger data
        passenger = pd.DataFrame([{
            "Pclass": pclass,
            "Sex": sex,
            "Age": age,
            "SibSp": sibsp,
            "Parch": parch,
            "Fare": fare,
            "Embarked": embarked
        }])

        # Predict survival
        prediction = model.predict(passenger)[0]

        probability = model.predict_proba(passenger)[0][1]

        result = (
            "Survived"
            if prediction == 1
            else "Did Not Survive"
        )

        return render_template(
            "index.html",
            pred=result,
            prob=f"{probability:.1%}",
            prob_width=f"{probability:.1%}",
            form=form_values,
            prediction_class="survived" if prediction == 1 else "not-survived"
        )

    except (ValueError, KeyError, TypeError):
        form_values = {
            "pclass": request.form.get("pclass", "3"),
            "sex": request.form.get("sex", "female"),
            "age": request.form.get("age", ""),
            "sibsp": request.form.get("sibsp", "0"),
            "parch": request.form.get("parch", "0"),
            "fare": request.form.get("fare", ""),
            "embarked": request.form.get("embarked", "S"),
        }
        return render_template(
            "index.html",
            error="Please enter valid passenger information.",
            form=form_values
        )


if __name__ == "__main__":
    app.run(debug=True)