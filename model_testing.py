import streamlit as st
import pandas as pd
import numpy as np
import ast
from model_testing1 import predict_with_area  # replace file name

# ---------------------------------------------------
# CLEAN LIST COLUMN FUNCTION
# ---------------------------------------------------
def clean_list_column(x):
    """
    Converts string representations of lists into real python lists.
    Handles cases like:
      "['1 B/R', '2 B/R']"
      "['0-5' '6-10' '11-20']"
    """
    if pd.isna(x):
        return []

    try:
        result = ast.literal_eval(x)
        if isinstance(result, list):
            return [str(i).strip() for i in result]
    except:
        pass

    # Remove brackets and quotes
    x = x.replace("[", "").replace("]", "").replace('"', '').replace("'", "").strip()
    
    # Split by whitespace but preserve multi-word items like '1 B/R'
    items = []
    buffer = ""
    for token in x.split():
        if buffer:
            buffer += " " + token
            items.append(buffer)
            buffer = ""
        else:
            if "/" in token or "-" in token or token.isalpha():
                items.append(token)
            else:
                buffer = token
    if buffer:
        items.append(buffer)
    return items

# ---------------------------------------------------
# LOAD RANGE FILE
# ---------------------------------------------------
range_df = pd.read_csv("column_input_ranges.csv")

# CLEAN LIST COLUMNS
list_cols = ["rooms_en", "floor_bin", "has_parking", "swimming_pool", "balcony", "elevator"]
for col in list_cols:
    range_df[col] = range_df[col].apply(clean_list_column)

# AREA LIST
area_list = range_df["area_name_en"].tolist()

# ---------------------------------------------------
# STREAMLIT UI
# ---------------------------------------------------
st.title("🏡 Dubai Real Estate Price Predictor (18 Areas)")

# Step 1 — Area Selection
area = st.selectbox("Select Area", ["-- Select Area --"] + area_list)

if area != "-- Select Area --":
    st.subheader(f"Enter Property Features for **{area}**")

    # Filter for selected row
    row = range_df[range_df["area_name_en"] == area].iloc[0]

    # YES/NO → 1/0
    to_bool = lambda x: 1 if x == "Yes" else 0

    # PROCEDURE AREA
    median_area = float(row["median_procedure_area"])
    min_area    = float(row["min"])
    max_area    = float(row["max"])

    procedure_area = st.number_input(
        "Procedure Area (sq.m)",
        min_value=min_area,
        max_value=max_area,
        value=median_area
    )

    # CLEANED DROPDOWN VALUES
    rooms_options = ["-- Select Room Type --"] + row["rooms_en"]
    floor_bin_options = ["-- Select Floor Range --"] + row["floor_bin"]

    # Default selection index
    rooms_en = st.selectbox("Number of Rooms", options=rooms_options, index=1)
    floor_bin = st.selectbox("Floor Level", options=floor_bin_options, index=1)

    # Boolean features
    has_parking   = to_bool(st.selectbox("Parking", ["Yes", "No"]))
    swimming_pool = to_bool(st.selectbox("Swimming Pool", ["Yes", "No"]))
    balcony       = to_bool(st.selectbox("Balcony", ["Yes", "No"]))
    elevator      = to_bool(st.selectbox("Elevator", ["Yes", "No"]))
    metro         = to_bool(st.selectbox("Metro Access", ["Yes", "No"]))

    # PREDICT BUTTON
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

            st.write("### Last 10 Months Forecast")
            st.dataframe(final_df.tail(10))

            df_chart = final_df.copy()
            df_chart["month"] = pd.to_datetime(df_chart["month"], errors="coerce")
            st.line_chart(df_chart.set_index("month")["median_price"])
