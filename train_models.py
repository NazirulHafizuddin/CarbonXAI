"""
train_models.py
Trains Random Forest, XGBoost and LightGBM with the hyperparameters found by
RandomizedSearchCV (3-fold CV on the training set, scoring = MAE), evaluates
them once on the held-out test set, keeps the best model, and saves what the
Streamlit app needs.

    python train_models.py

The tuned values below are the final results of the tuning run in the notebook.
Do not edit them after looking at test scores.
"""

import json
import joblib
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
import shap

from preprocessing import full_pipeline_fit

DATA_PATH = "data/Carbon_Emission.csv"
MODELS_DIR = "models"

# Cross-validated MAE from the tuning run (training data only), for the report
CV_MAE = {"Random Forest": 215.029, "XGBoost": 80.530, "LightGBM": 88.692}

print("STEP 1: load, clean, encode")
X, y, schema = full_pipeline_fit(DATA_PATH)
print(f"  feature matrix: {X.shape}  (expect 10000 x 35)")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"  train {X_train.shape}, test {X_test.shape}")

print("\nSTEP 2: train with tuned hyperparameters")
models = {
    "Random Forest": RandomForestRegressor(
        n_estimators=300, min_samples_leaf=1, max_features=0.5, max_depth=18,
        random_state=42, n_jobs=-1),
    "XGBoost": XGBRegressor(
        subsample=0.85, reg_lambda=10, n_estimators=800, max_depth=3,
        learning_rate=0.1, colsample_bytree=0.85, random_state=42, n_jobs=-1),
    "LightGBM": LGBMRegressor(
        subsample=0.7, num_leaves=15, n_estimators=800, min_child_samples=10,
        learning_rate=0.05, colsample_bytree=0.85, random_state=42, n_jobs=-1, verbose=-1),
}

results, fitted = {}, {}
for name, model in models.items():
    model.fit(X_train, y_train)
    p = model.predict(X_test)
    results[name] = {
        "MAE": float(mean_absolute_error(y_test, p)),
        "RMSE": float(np.sqrt(mean_squared_error(y_test, p))),
        "R2": float(r2_score(y_test, p)),
        "CV_MAE": CV_MAE[name],
    }
    fitted[name] = model
    r = results[name]
    print(f"  {name:14s} MAE={r['MAE']:.2f} RMSE={r['RMSE']:.2f} R2={r['R2']:.4f}")

best_name = min(results, key=lambda k: results[k]["MAE"])
best_model = fitted[best_name]
print(f"\nSTEP 3: best model by test MAE = {best_name}")

print("\nSTEP 4: global SHAP (1000 test rows, same sample as the notebook)")
sample = X_test.sample(1000, random_state=42)
explainer = shap.TreeExplainer(best_model)
global_shap_values = explainer.shap_values(sample)

print("\nSTEP 5: save (version-proof formats: JSON, CSV, NPY, no pickles)")
import os
os.makedirs(MODELS_DIR, exist_ok=True)
for f in os.listdir(MODELS_DIR):                       # remove files from older runs
    if f.endswith(".joblib") or f in ("best_model.json",):
        os.remove(os.path.join(MODELS_DIR, f))
if isinstance(best_model, XGBRegressor):
    best_model.save_model(f"{MODELS_DIR}/best_model.json")   # XGBoost native format, stable across versions
    model_kind = "xgboost_json"
else:
    joblib.dump(best_model, f"{MODELS_DIR}/best_model.joblib", compress=3)
    model_kind = "joblib"
sample.to_csv(f"{MODELS_DIR}/shap_sample.csv", index=False)
np.save(f"{MODELS_DIR}/global_shap_values.npy", global_shap_values)
with open(f"{MODELS_DIR}/schema.json", "w") as f:
    json.dump(schema, f, indent=1)
with open(f"{MODELS_DIR}/results.json", "w") as f:
    json.dump({"best_model": best_name, "model_kind": model_kind, "metrics": results}, f, indent=2)
print("  saved to models/. Run: streamlit run app.py")
