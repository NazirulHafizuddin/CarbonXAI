"""
preprocessing.py
Shared data cleaning + preprocessing pipeline for the Carbon Emission dataset.
Used identically by train_models.py (training) and app.py (live prediction)
so that one user input is encoded exactly the way the training data was.

Encoding strategy (final):
  - Ordered categories      -> ordinal integers (ORDINAL_MAPS)
  - Unordered categories    -> one-hot, first level dropped (NOMINAL_COLS)
  - Multi-value list fields -> binary indicator columns (MULTI_VALUE_COLS)
Result: 35 input features.
"""

import pandas as pd
import numpy as np

TARGET = "CarbonEmission"

MULTI_VALUE_COLS = ["Recycling", "Cooking_With"]

# Ordered categories, lowest to highest. The order for "How Often Shower" and
# "Body Type" is a modelling assumption (documented in the report).
ORDINAL_MAPS = {
    "Frequency of Traveling by Air": ["never", "rarely", "frequently", "very frequently"],
    "Waste Bag Size": ["small", "medium", "large", "extra large"],
    "How Often Shower": ["less frequently", "daily", "more frequently", "twice a day"],
    "Energy efficiency": ["No", "Sometimes", "Yes"],
    "Social Activity": ["never", "sometimes", "often"],
    "Body Type": ["underweight", "normal", "overweight", "obese"],
}

# No natural order -> one-hot. Listed explicitly (not detected by dtype) so the
# result does not depend on the pandas version (pandas 3 uses a "str" dtype).
NOMINAL_COLS = ["Sex", "Diet", "Heating Energy Source", "Transport", "Vehicle Type"]

# Prefixes used to map a one-hot / indicator column back to its original variable
GROUP_PREFIXES = [f"{c}_" for c in NOMINAL_COLS] + [f"{c}_" for c in MULTI_VALUE_COLS]

# Factors that describe the person, not a choice they can change. They stay in
# the model but are excluded from "what can you change" advice.
NON_ACTIONABLE = {"Sex", "Body Type"}


def group_name(feature: str) -> str:
    """Map an encoded column name back to its original variable."""
    for p in GROUP_PREFIXES:
        if feature.startswith(p):
            return p[:-1]
    return feature


def load_raw(csv_path: str) -> pd.DataFrame:
    return pd.read_csv(csv_path)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Cleaning: structural missing value fix + duplicate removal."""
    df = df.copy()

    # Vehicle Type is empty when the person has no private vehicle
    # (Transport = public or walk/bicycle). Structural, so it becomes its own level.
    if "Vehicle Type" in df.columns:
        df["Vehicle Type"] = df["Vehicle Type"].fillna("No_Vehicle")

    df = df.drop_duplicates().reset_index(drop=True)
    return df


def parse_multi_value_columns(df: pd.DataFrame, known_items: dict | None = None):
    """
    Expand string-encoded list columns (Recycling, Cooking_With) into binary
    indicator columns. At inference, known_items fixes the exact column set.
    """
    df = df.copy()
    items_map = {}

    for col in MULTI_VALUE_COLS:
        if col not in df.columns:
            continue
        parsed = (
            df[col].astype(str)
            .str.strip("[]")
            .str.replace("'", "", regex=False)
            .str.split(", ")
        )
        if known_items is not None:
            items = known_items[col]
        else:
            items = sorted({i for lst in parsed for i in lst if i and i != "nan"})
        items_map[col] = items

        for item in items:
            df[f"{col}_{item.replace(' ', '_')}"] = parsed.apply(lambda l, it=item: int(it in l))
        df = df.drop(columns=[col])

    return df, items_map


def encode_ordinal(df: pd.DataFrame) -> pd.DataFrame:
    """Map ordered categories to integers. Fails loudly on an unknown label."""
    df = df.copy()
    for col, order in ORDINAL_MAPS.items():
        if col not in df.columns:
            continue
        df[col] = df[col].map({v: i for i, v in enumerate(order)})
        if df[col].isna().any():
            raise ValueError(f"Unmapped value in ordinal column '{col}'")
    return df


def encode_nominal(df: pd.DataFrame, train_columns: list | None = None) -> pd.DataFrame:
    """
    One-hot encode the unordered columns.
    Training: drop_first=True.
    Inference: a single row has only one level per column, so drop_first would
    delete the very column that is set. Encode in full and reindex to the
    training columns instead; dropped reference levels vanish, which is the
    same as an all-zero row for them.
    """
    if train_columns is None:
        return pd.get_dummies(df, columns=NOMINAL_COLS, drop_first=True)
    out = pd.get_dummies(df, columns=NOMINAL_COLS, drop_first=False)
    return out.reindex(columns=train_columns, fill_value=0)


def full_pipeline_fit(csv_path: str):
    """
    Run once at training time.
    Returns X, y and a `schema` dict that reproduces the transformation later.
    """
    df = load_raw(csv_path)
    df = clean(df)
    df, items_map = parse_multi_value_columns(df)
    df = encode_ordinal(df)  # after this, ordinal columns are integers

    y = df[TARGET]
    X = encode_nominal(df.drop(columns=[TARGET]))

    raw = clean(load_raw(csv_path))
    numeric_cols = [
        c for c in raw.columns
        if c not in ORDINAL_MAPS and c not in NOMINAL_COLS
        and c not in MULTI_VALUE_COLS and c != TARGET
    ]
    schema = {
        "multi_value_items": items_map,
        "feature_columns": X.columns.tolist(),
        "ordinal_options": ORDINAL_MAPS,
        "nominal_options": {c: sorted(raw[c].unique().tolist()) for c in NOMINAL_COLS},
        "numeric_ranges": {c: (float(raw[c].min()), float(raw[c].max())) for c in numeric_cols},
        "numeric_defaults": {c: float(raw[c].median()) for c in numeric_cols},
        # In this dataset the distance range depends on the transport mode
        # (private 3-9999, public 0-2000, walk/bicycle 0-99), so the form uses these.
        "distance_by_transport": {
            t: (int(g.min()), int(g.max()), int(g.median()))
            for t, g in raw.groupby("Transport")["Vehicle Monthly Distance Km"]
        },
    }
    return X, y, schema


def transform_single_input(raw_row: dict, schema: dict) -> pd.DataFrame:
    """Raw form input (dict) -> 1-row DataFrame matching schema['feature_columns']."""
    df = pd.DataFrame([raw_row])
    df = clean(df)
    df, _ = parse_multi_value_columns(df, known_items=schema["multi_value_items"])
    df = encode_ordinal(df)
    return encode_nominal(df, train_columns=schema["feature_columns"])
