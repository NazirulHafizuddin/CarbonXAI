# CarbonXAI: Explainable Carbon Emission Prediction Dashboard

Streamlit dashboard for the FYP. It predicts individual carbon emission (kg CO2e per month)
from lifestyle inputs, compares Random Forest, XGBoost and LightGBM, and explains predictions
with SHAP (global and local).

Final results (80:20 split, random_state=42, 35 input features):

| Model | Test MAE | Test RMSE | Test R2 |
|---|---|---|---|
| XGBoost (best) | 77.22 | 104.54 | 0.9895 |
| LightGBM | 82.59 | 113.41 | 0.9876 |
| Random Forest | 204.47 | 267.09 | 0.9314 |

## Folder structure

```
carbon_dashboard/
  data/Carbon_Emission.csv
  models/            best_model.json, schema.json, SHAP sample and values, results.json (already included)
  preprocessing.py   shared cleaning and encoding (ordinal + one-hot)
  train_models.py    trains the 3 tuned models, keeps the best
  app.py             entry point: page config and routing (intro first, then dashboard)
  landing_page.py    intro page (one line, calls landing.py)
  landing.py         the scroll-based landing page: CSS, screens, FEEDBACK_URL and IMAGES settings
  dashboard.py       the dashboard (model, SHAP and page logic; was app.py before the landing page)
  assets/            put your own photos here (see IMAGES in landing.py)
  ui.py              styling and HTML cards (glass look); presentation only
  .streamlit/config.toml   theme and layout settings
  requirements.txt
```

## Run in VS Code

```bash
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
streamlit run app.py
```

The `models/` folder is already trained, so you can run the app straight away.
Model and data files use version-proof formats (XGBoost JSON, CSV, NPY, JSON), so they load on any
Python or library version. Only run `python train_models.py` if you change the data or the preprocessing.
It takes about a minute and should print XGBoost MAE=77.22.

## Deploy (Streamlit Community Cloud)

1. Push this folder to a GitHub repo, including `models/` and the `.streamlit` folder (all small).
2. On share.streamlit.io choose the repo and keep the main file as `app.py`.
3. Keep `streamlit==1.65.0` pinned (the styling depends on it).

## Encoding used (important for the report)

- Ordinal: Frequency of Traveling by Air, Waste Bag Size, How Often Shower, Energy efficiency,
  Social Activity, Body Type. The orders for How Often Shower and Body Type are assumptions.
- One-hot (first level dropped): Sex, Diet, Heating Energy Source, Transport, Vehicle Type.
- Binary indicators: Recycling and Cooking_With items.
- Live prediction encodes in full and reindexes to the training columns, because dropping the
  first level on a single row would erase the selected category.

## Interface

Live dashboard: inputs sit in the dark panel (Travel, Home, Lifestyle, Waste tabs) and the result, SHAP
explanation and "Where you can cut" levers update as soon as an input changes. The levers are the model's
estimate of the monthly change for one habit at a time, not guaranteed savings.
The styling targets Streamlit's own element names, so `streamlit==1.65.0` is pinned. If you upgrade
Streamlit, check the look again.

## Form behaviour

Transport mode is chosen first. For public transport or walk/bicycle the vehicle type shows
"None / Not applicable" (disabled) and the distance range follows the dataset (public 0 to 2,000 km,
walk/bicycle 0 to 99 km, private 3 to 9,999 km). Recycling and Cooking with can be left empty for none.

## Known limits

- The dataset appears synthetic (near uniform distributions, R2 close to 0.99), so scores are
  not a prediction of real world accuracy.
- Sex and Body Type rank high in SHAP, most likely a data generation artefact. The dashboard keeps
  them in the model but leaves them out of the "factors you can change" advice.
- SHAP shows what the model learned, not cause and effect.

## Landing page
- Opens first at `/`. The dashboard is at `/dashboard`. "Skip intro", "Go to dashboard" and "Proceed to dashboard" all open it.
- Module cards and "Start prediction" open a chosen dashboard page (the intro stores the page name in `st.session_state["_goto"]`).
- Feedback form link: set `FEEDBACK_URL` at the top of `landing.py`. While empty, the buttons are disabled placeholders.
- Photos: copy files into `assets/` and fill `IMAGES` in `landing.py` (hero, why, action, feedback). Without them the built-in vector art is used.
- Browsers without CSS scroll-driven animation show everything without the reveal effect.
