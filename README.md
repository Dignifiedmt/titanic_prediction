# Titanic Survival Predictor

A responsive Flask application serving a Random Forest classifier trained on the Titanic passenger dataset. It provides validated predictions, an interactive historical survival chart, and an in-form passenger profile summary.

## Project contents

```text
├── Titanic-Dataset.csv
├── Titanic_Model.ipynb
├── titanic_model.pkl
├── model_metadata.json
├── app.py
├── requirements.txt
├── templates/
│   ├── index.html
│   └── 404.html
└── static/
    ├── css/style.css
    ├── css/analytics.css
    └── js/script.js
```

## Run locally

Use Python 3.11 or newer and the compatible dependencies in `requirements.txt`:

```bash
python -m venv .venv
# Activate the virtual environment, then:
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000/. `/health` reports application health, and `/api/analytics` returns the aggregated chart data as JSON.

## Smart features and chart

- The model validates input values server-side (including non-finite numeric values) and returns probabilities for both outcomes.
- The profile helper summarizes age band, ticket class, and travel-party size without claiming those fields explain or cause a prediction.
- The chart calculates observed survival rates by passenger class and sex from `Titanic-Dataset.csv`, with an interactive sex filter and group sizes in bar tooltips.
- Test accuracy and F1 score are read from `model_metadata.json` when available.
- Chart associations are descriptive historical summaries, not causal findings. Estimated probabilities are not guaranteed to be calibrated.

## Train or retrain

Open `Titanic_Model.ipynb` and run the notebook cells from top to bottom. The saved pipeline and metadata should be generated in the project directory. Keep Python, NumPy, Pandas, and Scikit-learn versions compatible with the serialized model.

## Security and deployment

Only load `titanic_model.pkl` if you created it or obtained it from a trusted source: Pickle files can execute code during loading. `debug=True` is intended for local development only; disable it for public deployment and use a production WSGI server with appropriate security controls.
