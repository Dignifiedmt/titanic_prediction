# Titanic Survival Predictor

A responsive Flask web application that serves a Random Forest classification pipeline trained in a Jupyter Notebook. The interface includes light/dark themes, responsive layouts, client-side interactions, and a survival-class probability display.

## Project contents

```text
titanic-predictor/
├── Titanic-Dataset.csv
├── Titanic_Model.ipynb
├── titanic_model.pkl
├── model_metadata.json
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── templates/
│   ├── index.html
│   └── 404.html
└── static/
    ├── css/style.css
    └── js/script.js
```

## Requirements

- Python 3.11 or newer is recommended.
- Use the dependency versions in `requirements.txt` when loading the included Pickle model. Pickle is Python-version and library-version sensitive.

## Windows setup (PowerShell)

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, use Command Prompt and run `.venv\Scripts\activate.bat`.

## Train or retrain the model

1. Open `Titanic_Model.ipynb` in VS Code (with the Jupyter extension) or Jupyter Notebook.
2. Select the Python environment where you installed `requirements.txt`.
3. Run the notebook cells from top to bottom. It is arranged into **10 main steps**.
4. Step 10 writes `titanic_model.pkl` and `model_metadata.json` in the notebook's working directory.

The notebook uses the seven same features as the Flask form: `Pclass`, `Sex`, `Age`, `SibSp`, `Parch`, `Fare`, and `Embarked`. The saved object is a complete Scikit-learn pipeline, including imputers, one-hot encoding, and the classifier.

## Start Flask

From the project root, run:

```powershell
python app.py
```

Open http://127.0.0.1:5000/ in your browser. The `/health` endpoint returns a basic application health status.

## Model and evaluation notes

- The notebook reserves 20% of the data as a stratified test set.
- Reported metrics are calculated from the supplied CSV when the notebook runs; they are not hardcoded.
- Feature importance is a model-inspection aid, not evidence of causation.
- The probability shown by the web application is the classifier's estimated probability for the survival class. It is not guaranteed to be calibrated.
- This is an educational demonstration using historical data, not a source of historical certainty.

## Security and deployment

- Only load `titanic_model.pkl` if you created it or obtained it from a trusted source. Pickle files can execute code during loading.
- Keep Python, NumPy, Pandas, and Scikit-learn versions compatible between training and serving. The included dependency file pins the core versions used for the included model.
- `debug=True` is enabled for local development only. Turn debug mode off for public deployment.
- For a production deployment, use a production WSGI server such as Gunicorn (typically on Linux), configure HTTPS, and add appropriate security controls.

## Author

Khadija Muhammad Tasiu
