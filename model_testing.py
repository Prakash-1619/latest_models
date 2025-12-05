import streamlit as st
import pandas as pd
import numpy as np

from your_module_file import predict_with_area   # replace file name

# Load ranges file
range_df = pd.read_csv("column_input_ranges.csv")

# Convert string lists → real Python lists
def fix_list(x):
    try:
        x = x.strip("[]").replace("'", "")
        return [i.strip() for i in x.split()]
    except:
        return []

range_df["rooms_en"]      = range_df["rooms_en"].apply(fix_list)
range_df["floor_bin"]     = range_df["floor_bin"].apply(fix_list)
range_df["has_parking"]   = range_df["has_parking"].apply(fix_list)
range_df["swimming_pool"] = range_df["swimming_pool"].apply(fix_list)
range_df["balcony"]       = range_df["balcony"].apply(fix_list)
range_df["elevator"]      = range_df["elevator"].apply(fix_list)

# AREA LIST
area_list = range_df["area_name_en"].tolist()

st.title("🏡 Dubai Real Estate Price Predictor (18 Areas)")

# Step 1 — Area Selection
area = st.selectbox("Select Area", ["-- Select Area --"] + area_list)

if area != "-- Select Area --":
    st.subheader(f"Enter Property Features for **{area}**")

    # Filter row for this area
    row = range_df[range_df["area_name_en"] == area].iloc[0]

    # YES/NO → 1/0
    to_bool = lambda x: 1 if x == "Yes" else 0

    # --------------------------
    # PROCEDURE AREA INPUT
    # --------------------------
    median_area = float(row["median_procedure_area"])
    min_area    = float(row["min"])
    max_area    = float(row["max"])

    procedure_area = st.number_input(
        "Procedure Area (sq.m)",
        min_value=min_area,
        max_value=max_area,
        value=median_area
    )

    # --------------------------
    # CATEGORY OPTIONS
    # --------------------------
    rooms_en     = st.selectbox("Room Type", row["rooms_en"])
    floor_bin    = st.selectbox("Floor Range", row["floor_bin"])

    has_parking  = to_bool(st.selectbox("Parking", ["Yes", "No"]))
    swimming_pool = to_bool(st.selectbox("Swimming Pool", ["Yes", "No"]))
    balcony       = to_bool(st.selectbox("Balcony", ["Yes", "No"]))
    elevator      = to_bool(st.selectbox("Elevator", ["Yes", "No"]))
    metro         = to_bool(st.selectbox("Metro Access", ["Yes", "No"]))

    # --------------------------
    # PREDICT BUTTON
    # --------------------------
    if st.button("Predict Price"):
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

        final_df = predict_with_area(input_data)

        if final_df is not None:
            st.success("✅ Prediction Successful!")
            st.dataframe(final_df.tail(10))

            df_chart = final_df.copy()
            df_chart["month"] = pd.to_datetime(df_chart["month"], errors="coerce")
            st.line_chart(df_chart.set_index("month")["median_price"])
