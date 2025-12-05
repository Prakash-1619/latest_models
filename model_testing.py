import streamlit as st
import pandas as pd
import numpy as np
import os
import pickle
from statsmodels.nonparametric.smoothers_lowess import lowess

# -----------------------------------------------------
# 1. DIRECTORIES
# -----------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(BASE_DIR, "dt_models")
trained_dir = os.path.join(BASE_DIR, "trained_columns")

# -----------------------------------------------------
# 2. Load Training Columns
# -----------------------------------------------------
def load_columns(area_name_en):
    area_name_en = area_name_en.replace("_", " ").strip()

    for f in os.listdir(trained_dir):
        if f.lower() == f"trained_columns_{area_name_en}.pkl".lower() or \
           f.lower() == f"trained_columns_{area_name_en.replace(' ', '_')}.pkl".lower():
            with open(os.path.join(trained_dir, f), "rb") as file:
                return pickle.load(file)

    st.error(f"❌ Trained columns file missing for area: {area_name_en}")
    return None


# -----------------------------------------------------
# 3. Load Decision Tree Model
# -----------------------------------------------------
def load_model(area_name_en):
    area_name_en = area_name_en.replace("_", " ").strip()

    for f in os.listdir(models_dir):
        if f.lower() == f"dt_model_{area_name_en}.pkl".lower() or \
           f.lower() == f"dt_model_{area_name_en.replace(' ', '_')}.pkl".lower():
            with open(os.path.join(models_dir, f), "rb") as file:
                return pickle.load(file)

    st.error(f"❌ Model file missing for area: {area_name_en}")
    return None


# -----------------------------------------------------
# 4. Prediction Function
# -----------------------------------------------------
def predict_with_area(input_data):

    forecast_df = pd.read_csv(os.path.join(BASE_DIR, "Sarima_forecast_6M.csv"))
    historic_df = pd.read_csv(os.path.join(BASE_DIR, "historical_df.csv"))

    area = input_data["area_name_en"].replace("_", " ").strip()

    # Load model + expected columns
    train_columns = load_columns(area)
    model = load_model(area)

    if train_columns is None or model is None:
        return None

    # One-hot encode
    temp = pd.DataFrame([input_data])
    temp["area_name_en"] = area
    temp = pd.get_dummies(temp)

    # Add missing columns
    for col in train_columns:
        if col not in temp.columns:
            temp[col] = 0

    temp = temp[train_columns]

    # Predict base median price
    predicted_price = model.predict(temp)[0]

    # Forecast section
    forecast_area = forecast_df[forecast_df["area_name_en"] == area].copy()
    forecast_area["median_price"] = predicted_price * forecast_area["growth_factor"]
    forecast_area = forecast_area[["month", "median_price"]]

    # Historic section
    historic_area = historic_df[historic_df["area_name_en"] == area].copy()

    if not historic_area.empty:
        historic_area = historic_area.sort_values("month").reset_index(drop=True)

        smoothed = lowess(
            endog=historic_area["median_price"].values,
            exog=np.arange(len(historic_area)),
            frac=0.04
        )

        historic_area["median_price"] = smoothed[:, 1]

        if not forecast_area.empty:
            historic_area.loc[historic_area.index[-1], "median_price"] = forecast_area.iloc[0]["median_price"]

    final_df = pd.concat([historic_area[["month", "median_price"]], forecast_area], ignore_index=True)
    return final_df


# -----------------------------------------------------
# 5. STREAMLIT UI
# -----------------------------------------------------
st.title("🏡 Real Estate Price Predictor (Decision Tree + SARIMA Forecast)")
st.write("Predict next 6 months median sale price for Dubai areas.")

# Load area list dynamically
available_areas = sorted([
    f.replace("dt_model_", "").replace(".pkl", "").replace("_", " ").strip()
    for f in os.listdir(models_dir)
    if f.endswith(".pkl")
])

area = st.selectbox("Select Area", available_areas)

# User Inputs
st.subheader("Enter Property Details")

procedure_area = st.number_input("Procedure Area (sq.m)", min_value=20, max_value=2000, value=100)
room = st.number_input("Rooms", min_value=1, max_value=10, value=2)
bath = st.number_input("Bathrooms", min_value=1, max_value=10, value=2)

# Convert YES/NO → 1/0
def yes_no_to_binary(x):
    return 1 if x == "Yes" else 0

swimming_pool = yes_no_to_binary(st.selectbox("Swimming Pool", ["No", "Yes"]))
balcony = yes_no_to_binary(st.selectbox("Balcony", ["No", "Yes"]))
elevator = yes_no_to_binary(st.selectbox("Elevator", ["No", "Yes"]))
metro = yes_no_to_binary(st.selectbox("Metro Access", ["No", "Yes"]))
has_parking = yes_no_to_binary(st.selectbox("Parking", ["No", "Yes"]))

if st.button("Predict Price"):
    input_data = {
        "area_name_en": area,
        "procedure_area": procedure_area,
        "room": room,
        "bath": bath,
        "balcony": balcony,
        "elevator": elevator,
        "parking": has_parking,
        "swimming_pool": swimming_pool,
        "metro": metro
    }

    result = predict_with_area(input_data)

    if result is not None:
        st.success("Prediction successful!")
        st.write(result)

        # Line chart
        st.line_chart(result.set_index("month")["median_price"])

