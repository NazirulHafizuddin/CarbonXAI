"""
app.py
CarbonXAI: Explainable Carbon Emission Prediction Dashboard.

    streamlit run app.py

Needs models/ to exist. Run `python train_models.py` first.
Styling and HTML building blocks are in ui.py. Model and SHAP logic stays here.
"""

import json
import joblib
import numpy as np
import pandas as pd
import streamlit as st
import shap
from xgboost import XGBRegressor

import ui
from preprocessing import transform_single_input, group_name, NON_ACTIONABLE

st.set_page_config(
    page_title="CarbonXAI | Carbon Emission Prediction",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown(ui.CSS, unsafe_allow_html=True)


# ─────────────────────────── artifacts ───────────────────────────
@st.cache_resource
def load_artifacts():
    with open("models/results.json") as f:
        results = json.load(f)
    if results.get("model_kind") == "xgboost_json":
        model = XGBRegressor()
        model.load_model("models/best_model.json")     # native format, works across versions
    else:
        model = joblib.load("models/best_model.joblib")
    shap_sample = pd.read_csv("models/shap_sample.csv")
    global_shap_values = np.load("models/global_shap_values.npy")
    with open("models/schema.json") as f:
        schema = json.load(f)
    explainer = shap.TreeExplainer(model)          # rebuilt at start
    ref_preds = model.predict(shap_sample)         # reference distribution for percentiles
    return model, explainer, shap_sample, global_shap_values, schema, results, ref_preds


try:
    model, explainer, shap_sample, global_shap_values, schema, results, ref_preds = load_artifacts()
except FileNotFoundError:
    st.error("Trained model not found. Run `python train_models.py` in this folder, "
             "then restart the dashboard.")
    st.stop()

best_name = results["best_model"]
mae = results["metrics"][best_name]["MAE"]
avg_pred = float(np.ravel(explainer.expected_value)[0])
ordinal_opts = schema["ordinal_options"]
nominal_opts = schema["nominal_options"]
num_range = schema["numeric_ranges"]
num_default = schema["numeric_defaults"]


def label(v):
    return str(v).replace("_", " ").capitalize()


def grouped_local(shap_row, columns):
    """Sum one-hot / indicator columns back to their original variable."""
    return pd.Series(shap_row, index=columns).groupby(group_name).sum()


def grouped_global(sv, columns):
    df = pd.DataFrame(sv, columns=columns)
    return df.T.groupby(group_name).sum().T.abs().mean()


# ─────────────────────────── top bar ───────────────────────────
PAGES = ["Prediction", "Model comparison", "SHAP explanations", "Sustainability insights"]
c_left, c_mid, c_right = st.columns([1.1, 2.6, 1.1], vertical_alignment="center")
with c_left:
    st.markdown(ui.brand(), unsafe_allow_html=True)
with c_mid:
    page = st.segmented_control("Navigate", PAGES, default="Prediction", key="nav",
                                label_visibility="collapsed") or "Prediction"
with c_right:
    st.markdown(ui.model_chip(best_name), unsafe_allow_html=True)


# ═════════════════════════ PREDICTION ═════════════════════════
if page == "Prediction":
    left, right = st.columns([4.3, 7.7], gap="large")

    with left:
        st.markdown(ui.hero("Your carbon<br>footprint",
                            "Adjust your lifestyle and the estimate updates straight away, "
                            "with the reasons behind it."), unsafe_allow_html=True)

        def slider(name, text, key):
            lo, hi = int(num_range[name][0]), int(num_range[name][1])
            return st.slider(text, lo, hi, int(num_default[name]), key=key)

        def ordinal(name, text, key, default_idx=1):
            opts = ordinal_opts[name]
            return st.select_slider(text, options=opts, value=opts[default_idx],
                                    format_func=label, key=key)

        with st.container(key="controls"):
            t_travel, t_home, t_life, t_waste = st.tabs(["Travel", "Home", "Lifestyle", "Waste"])

            with t_travel:
                transport = st.selectbox("Transport mode", nominal_opts["Transport"],
                                         index=nominal_opts["Transport"].index("private"),
                                         format_func=label, key="transport")
                has_vehicle = transport == "private"
                d_lo, d_hi, d_mid = schema["distance_by_transport"][transport]
                distance = st.number_input("Monthly distance traveled (km)", min_value=d_lo, max_value=d_hi,
                                           value=d_mid, step=1 if d_hi <= 100 else 50, key=f"dist_{transport}")
                if has_vehicle:
                    vehicle_type = st.selectbox(
                        "Vehicle type", [v for v in nominal_opts["Vehicle Type"] if v != "No_Vehicle"],
                        format_func=label, key="vehicle")
                else:
                    vehicle_type = st.selectbox("Vehicle type", ["No_Vehicle"], disabled=True,
                                                format_func=lambda v: "None / Not applicable", key="vehicle_na")
                    st.caption(f"With {label(transport).lower()} there is no private vehicle. "
                               f"Distance is limited to 0 to {d_hi:,} km, as in the dataset.")
                air_travel = ordinal("Frequency of Traveling by Air", "Flying", "air")

            with t_home:
                heating = st.selectbox("Heating energy source", nominal_opts["Heating Energy Source"],
                                       format_func=label, key="heating")
                energy_eff = ordinal("Energy efficiency", "Energy efficient equipment", "eff")
                tv_pc = slider("How Long TV PC Daily Hour", "TV / PC hours per day", "tv")
                internet = slider("How Long Internet Daily Hour", "Internet hours per day", "net")
                cooking = st.multiselect("Cooking with (leave empty for none)",
                                         ["Airfryer", "Grill", "Microwave", "Oven", "Stove"], key="cook")

            with t_life:
                diet = st.selectbox("Diet", nominal_opts["Diet"], format_func=label, key="diet")
                sex = st.selectbox("Sex", nominal_opts["Sex"], format_func=label, key="sex")
                body_type = ordinal("Body Type", "Body type", "body")
                social = ordinal("Social Activity", "Social activity", "social")
                shower = ordinal("How Often Shower", "Showering", "shower")
                new_clothes = slider("How Many New Clothes Monthly", "New clothes per month", "clothes")
                grocery = slider("Monthly Grocery Bill", "Monthly grocery bill", "grocery")

            with t_waste:
                waste_size = ordinal("Waste Bag Size", "Waste bag size", "wsize")
                waste_count = slider("Waste Bag Weekly Count", "Waste bags per week", "wcount")
                recycling = st.multiselect("Recycling (leave empty for none)",
                                           ["Glass", "Metal", "Paper", "Plastic"], key="recycle")

    # ---- run the model on the current inputs ----
    raw_input = {
        "Body Type": body_type, "Sex": sex, "Diet": diet,
        "How Often Shower": shower, "Heating Energy Source": heating,
        "Transport": transport, "Vehicle Type": vehicle_type if has_vehicle else "No_Vehicle",
        "Social Activity": social, "Monthly Grocery Bill": grocery,
        "Frequency of Traveling by Air": air_travel,
        "Vehicle Monthly Distance Km": distance, "Waste Bag Size": waste_size,
        "Waste Bag Weekly Count": waste_count, "How Long TV PC Daily Hour": tv_pc,
        "How Many New Clothes Monthly": new_clothes,
        "How Long Internet Daily Hour": internet, "Energy efficiency": energy_eff,
        "Recycling": str(recycling), "Cooking_With": str(cooking),
    }

    def predict(raw):
        return float(model.predict(transform_single_input(raw, schema))[0])

    X_input = transform_single_input(raw_input, schema)
    prediction = float(model.predict(X_input)[0])
    local = grouped_local(explainer.shap_values(X_input)[0], X_input.columns)
    pct = float((ref_preds < prediction).mean() * 100)
    level = "HIGH" if pct >= 66 else ("MEDIUM" if pct >= 33 else "LOW")
    delta = prediction - avg_pred

    def what_ifs():
        """Model estimate of the monthly change for single habit changes."""
        found = []
        air = ordinal_opts["Frequency of Traveling by Air"]
        i = air.index(air_travel)
        if i > 0:
            found.append(("Fly less often", f"{label(air[i])} to {label(air[i - 1])}",
                          {"Frequency of Traveling by Air": air[i - 1]}))
        if distance > 0:
            found.append(("Travel 25% fewer km", f"{distance:,} to {int(distance * 0.75):,} km",
                          {"Vehicle Monthly Distance Km": int(distance * 0.75)}))
        if has_vehicle and vehicle_type != "electric":
            found.append(("Switch to an electric vehicle", f"{label(vehicle_type)} to electric",
                          {"Vehicle Type": "electric"}))
        if heating != "electricity":
            found.append(("Heat with electricity", f"{label(heating)} to electricity",
                          {"Heating Energy Source": "electricity"}))
        if len(recycling) < 4:
            found.append(("Recycle all four materials", "Glass, metal, paper, plastic",
                          {"Recycling": str(["Glass", "Metal", "Paper", "Plastic"])}))
        if new_clothes > 0:
            found.append(("Buy 25% fewer clothes", f"{new_clothes} to {int(new_clothes * 0.75)} a month",
                          {"How Many New Clothes Monthly": int(new_clothes * 0.75)}))
        if waste_count > 1:
            found.append(("One less waste bag a week", f"{waste_count} to {waste_count - 1} bags",
                          {"Waste Bag Weekly Count": waste_count - 1}))
        scored = []
        for title, sub, change in found:
            d = predict({**raw_input, **change}) - prediction
            if d < -1:
                scored.append((d, title, sub))
        return sorted(scored)[:3]

    levers = what_ifs()

    # ---- results grid ----
    with right:
        sign_cls = "up" if delta >= 0 else "down"
        delta_txt = (f"{ui.fmt(abs(delta))} kg above the dataset average" if delta >= 0
                     else f"{ui.fmt(abs(delta))} kg below the dataset average")
        lo, hi = prediction - mae, prediction + mae
        html = (
            "<div class='cx-grid'>"
            "<div class='cx-card cx-main'><div class='cx-label'>Predicted emission</div>"
            f"<div class='cx-big'>{ui.fmt(prediction)}<small>kg CO₂e per month</small></div>"
            f"<span class='cx-delta {sign_cls}'>{delta_txt}</span>"
            f"{ui.dot_strip(pct)}"
            f"<div class='cx-strip-cap'><span>Lower</span><span>Higher than {pct:.0f}% of the reference sample</span></div></div>"
            "<div class='cx-pinkwrap'><div class='cx-pink'>"
            f"{ui.pink_art()}<div class='lab'>Emission level</div>"
            f"<span class='lvl'>{level}</span>"
            "<div class='glass'>"
            f"<div class='pct'>{pct:.0f}<span style='font-size:26px'>%</span></div>"
            f"<div class='cap'>of people in the reference sample have a lower estimate than this</div></div></div></div>"
            "<div class='cx-card'><div class='cx-label'>Typical model error</div>"
            f"<div class='cx-big' style='font-size:46px'>±{mae:.0f}<small>kg</small></div>"
            f"<div class='cx-note'>Average error on 2,000 unseen records. A fair range here is {ui.fmt(lo)} to {ui.fmt(hi)} kg.</div></div>"
            "<div class='cx-card'><div class='cx-label'>Dataset average</div>"
            f"<div class='cx-big' style='font-size:46px'>{ui.fmt(avg_pred)}<small>kg</small></div>"
            f"<div class='cx-note'>Your estimate is {prediction / avg_pred * 100:.0f}% of the average. "
            "SHAP bars below add up to the gap between the two.</div></div>"
            "<div class='cx-card cx-shapcard'><div class='cx-label'>What drives this estimate</div>"
            f"<div style='margin-top:10px'>{ui.shap_rows(local, 8)}</div>"
            "<div class='cx-legend'><span><b style='background:#E2487A'></b>Raises the estimate</span>"
            "<span><b style='background:#5E8C14'></b>Lowers the estimate</span></div>"
            "<div class='cx-note'>Related columns are combined into one factor. SHAP shows what the model learned from this "
            "dataset, not cause and effect.</div></div>"
            "</div>"
        )
        st.markdown(html, unsafe_allow_html=True)

    # ---- bottom band: what-if levers ----
    tiles = []
    for i, (d, title, sub) in enumerate(levers):
        tiles.append(
            "<div class='cx-tile'>" + ui.tile_art(i) +
            f"<div class='t'>{title}</div><div class='s'>{sub}</div>"
            f"<div class='glass'><span class='sv'>−{abs(d):,.0f}</span><span class='un'>kg CO₂e per month</span></div></div>")
    while len(tiles) < 3:
        tiles.append("<div class='cx-tile empty'><div class='t'>Already low here</div>"
                     "<div class='s'>No other single change shows a clear saving for these inputs.</div></div>")
    ratio = prediction / avg_pred
    band = (
        "<div class='cx-band'><div><h3>Where you can cut</h3>"
        "<p>The model's estimate of the monthly change if you adjust one habit and keep everything else the same.</p></div>"
        f"<div class='cx-tiles'>{''.join(tiles)}</div>"
        f"{ui.gauge(ratio / 2, f'{ratio:.2f}', '× average', 'Your estimate against the dataset average')}</div>"
        "<div class='cx-foot'>These are model estimates from a dataset that appears synthetic. They show association "
        "in the data, not guaranteed savings for a real household.</div>"
    )
    st.markdown(band, unsafe_allow_html=True)


# ═════════════════════════ MODEL COMPARISON ═════════════════════════
elif page == "Model comparison":
    st.markdown(ui.hero("Model<br>comparison",
                        "Random Forest, XGBoost and LightGBM, each tuned with 3-fold cross validation on the training "
                        "set and scored once on the same held-out test set (20 percent of the data)."),
                unsafe_allow_html=True)
    ranked = sorted(results["metrics"].items(), key=lambda kv: kv[1]["MAE"])
    cards = []
    for name, m in ranked:
        is_best = name == best_name
        badge = "<span class='cx-badge'>Best model</span><br>" if is_best else ""
        cards.append(
            f"<div class='cx-model{' best' if is_best else ''}'>{badge}<div class='cx-label'>{name}</div>"
            f"<div class='cx-big'>{m['MAE']:.2f}<small>kg MAE</small></div>"
            f"<div class='row'><span>RMSE</span><b>{m['RMSE']:.2f}</b></div>"
            f"<div class='row'><span>R²</span><b>{m['R2']:.4f}</b></div>"
            f"<div class='row'><span>Cross-validated MAE</span><b>{m['CV_MAE']:.2f}</b></div></div>")
    st.markdown(f"<div class='cx-models'>{''.join(cards)}</div>", unsafe_allow_html=True)

    top = max(m["RMSE"] for m in results["metrics"].values())
    bars = ""
    for name, m in ranked:
        for metric in ("MAE", "RMSE"):
            cls = "f b" if name == best_name else "f"
            bars += (f"<div class='cx-hbar'><span>{name} {metric}</span><div class='tr'>"
                     f"<div class='{cls}' style='width:{m[metric] / top * 100:.1f}%'></div></div>"
                     f"<b>{m[metric]:.1f}</b></div>")
    st.markdown("<div class='cx-card' style='margin-top:16px'><div class='cx-label'>Test error in kg CO₂e, lower is better</div>"
                f"<div style='margin-top:10px'>{bars}</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='cx-warn'>Scores are very high because this public dataset appears synthetic, with emissions "
                "that follow a clean formula. Use them to compare the models, not as the accuracy to expect on real survey "
                "data. The gap between XGBoost and LightGBM is small.</div>", unsafe_allow_html=True)


# ═════════════════════════ GLOBAL SHAP ═════════════════════════
elif page == "SHAP explanations":
    st.markdown(ui.hero("What drives<br>emissions",
                        f"Average influence of each factor across {len(shap_sample)} test records, "
                        f"using the {best_name} model."), unsafe_allow_html=True)
    view = st.segmented_control("View", ["By original factor", "By encoded column"],
                                default="By original factor", key="shapview") or "By original factor"
    if view == "By original factor":
        imp = grouped_global(global_shap_values, shap_sample.columns)
    else:
        imp = pd.Series(np.abs(global_shap_values).mean(axis=0), index=shap_sample.columns)
    imp = imp.sort_values(ascending=False).head(12)
    top = float(imp.max())
    rows = "".join(
        f"<div class='cx-dbar'><div class='nm'>{name}</div><div class='tr'><div class='f' style='width:{v / top * 100:.1f}%'></div></div>"
        f"<div class='v'>{v:,.0f} kg</div></div>" for name, v in imp.items())
    st.markdown("<div class='cx-dark'><div class='cx-label'>Mean absolute SHAP value, kg CO₂e</div>"
                f"<div style='margin-top:12px'>{rows}</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='cx-warn'>The original factor view adds up the columns that came from one question (for example "
                "all vehicle types), so multi-option questions are not underrated. SHAP explains what the model learned, not "
                "real-world cause and effect. Sex and body type rank high because the dataset's emission values depend on "
                "them, which is most likely how the data was produced.</div>", unsafe_allow_html=True)


# ═════════════════════════ SUSTAINABILITY INSIGHTS ═════════════════════════
elif page == "Sustainability insights":
    st.markdown(ui.hero("Sustainability<br>insights",
                        "Factors people can change, ranked by their average influence on the estimate. Aligned with "
                        "SDG 13, Climate Action."), unsafe_allow_html=True)
    imp = grouped_global(global_shap_values, shap_sample.columns)
    actionable = imp[[g for g in imp.index if g not in NON_ACTIONABLE]].sort_values(ascending=False).head(5)
    tiles = "".join(
        f"<div class='cx-tile'>{ui.tile_art(i)}<div class='t'>{feat}</div><div class='s'>Rank {i + 1}</div>"
        f"<div class='glass'><span class='sv'>{v:,.0f}</span><span class='un'>kg average impact</span></div></div>"
        for i, (feat, v) in enumerate(actionable.items()))
    st.markdown(f"<div class='cx-rank'>{tiles}</div>", unsafe_allow_html=True)
    st.markdown("<div class='cx-warn'>Driving distance and air travel are far ahead of every other lifestyle factor in "
                "this dataset, so they are the first places to look when reducing an individual footprint. Sex and body type "
                "are left out of this list because they are not behaviours a person can change, even though the model uses "
                "them. The data appears synthetic, so use the ranking to show how the method works, not as measured advice "
                "for real households.</div>", unsafe_allow_html=True)
