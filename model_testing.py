import streamlit as st
import pandas as pd
import numpy as np

# ------------------------------------------------------
# IMPORT YOUR MODEL FUNCTION
# ------------------------------------------------------
# Replace "model_testing" with the actual python file name in your repo
from model_testing1 import predict_with_area   

# ------------------------------------------------------
# AREA LIST (18 AREAS)
# ------------------------------------------------------
area_list = [
    'Al Barsha South Fifth',
    'Al Barsha South Fourth',
    'Al Barshaa South Third',
    'Al Hebiah Fourth',
    'Al Khairan First',
    'Al Merkadh',
    'Al Thanyah Fifth',
    'Al Yelayiss 2',
    'Burj Khalifa',
    'Business Bay',
    'Hadaeq Sheikh Mohammed Bin Rashid',
    'Jabal Ali First',
    'Madinat Al Mataar',
    'Madinat Dubai Almelaheyah',
    'Marsa Dubai',
    "Me'Aisem First",
    'Nadd Hessa',
    'Wadi Al Safa 5'
]

# ------------------------------------------------------
# STREAMLIT UI
# ------------------------------------------------------
st.title("🏡 Dubai Real Estate Price Predictor (18 Areas)")


# STEP 1 — AREA DROPDOWN
area = st.selectbox("Select Area", ["-- Select Area --"] + area_list)


# SHOW OTHER FEATURES ONLY WHEN AREA IS SELECTED
if area != "-- Select Area --":

    st.subheader(f"Enter Property Features for **{area}**")

    # Helper function: Yes/No → 1/0
    to_bool = lambda x: 1 if x == "Yes" else 0

    # --------------------------
    # INPUT FIELDS
    # --------------------------
    procedure_area = st.number_input(
        "Procedure Area (sq.m)",
        min_value=20,
        max_value=2000,
        value=80
    )

    has_parking = to_bool(st.selectbox("Parking", ["Yes", "No"]))

    floor_bin = st.selectbox(
        "Floor Range",
        ["0-5", "6-10", "11-20", "21-40", "40+"]
    )

    rooms_en = st.selectbox(
        "Room Type",
        ["Studio", "1BR", "2BR", "3BR", "4BR"]
    )

    swimming_pool = to_bool(st.selectbox("Swimming Pool", ["Yes", "No"]))
    balcony       = to_bool(st.selectbox("Balcony", ["Yes", "No"]))
    elevator      = to_bool(st.selectbox("Elevator", ["Yes", "No"]))
    metro         = to_bool(st.selectbox("Metro Access", ["Yes", "No"]))


    # -----------------------------------------
    # STEP 3 — PREDICTION BUTTON
    # -----------------------------------------
    if st.button("Predict Price"):

        # Build input dict
        input_data = {
            "area_name_en": area,
            "procedure_area": procedure_area,
            "has_parking": has_parking,
            "floor_bin": floor_bin,
            "rooms_en": rooms_en,
            "swimming_pool": swimming_pool,
            "balcony": balcony,
            "elevator": elevator,
            "metro": metro
        }

        # Run prediction
        final_df = predict_with_area(input_data)

        # -----------------------------------------
        # STEP 4 — DISPLAY RESULTS
        # -----------------------------------------
        if final_df is not None:
            st.success("✅ Prediction Successful!")

            st.write("### 📈 Forecasted Prices (Last 10 Months)")
            st.dataframe(final_df.tail(10))

            # Chart
            df_chart = final_df.copy()
            df_chart["month"] = pd.to_datetime(df_chart["month"], errors="coerce")
            df_chart = df_chart.set_index("month")

            st.line_chart(df_chart["median_price"])
        else:
            st.error("❌ Prediction failed. Check model logs.")
