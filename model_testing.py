import streamlit as st
import pandas as pd
import numpy as np
import ast
from model_testing1 import predict_with_area  # replace file name




# ---------------------------------------------------
# LOAD RANGE FILE
# ---------------------------------------------------
range_df = pd.read_csv("column_input_ranges.csv")

# CLEAN LIST COLUMNS
#list_cols = ["rooms_en", "floor_bin", "has_parking", "swimming_pool", "balcony", "elevator"]
#for col in list_cols:
    #range_df[col] = range_df[col].apply(clean_list_column)

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
    rooms_options = ['1 B/R', 'Studio', '2 B/R', '3 B/R', 'PENTHOUSE', 'More than 3B/R'] #row['rooms_en'].tolist()
    
    floor_bin_options = ['1-10', '11-20', '41-50', '21-30', 'Below 1st floor', '31-40',
                       '51-60', 'Other', '-9-0', '61-70', 'Top floor', '91-100', '81-90',
                       '71-80', 'Duplex']#row['floor_bin'].tolist()
        
    default_index = 1   
    rooms_en = st.selectbox("Number of Rooms", options=rooms_options)# index= default_index)
    floor_bin = st.selectbox("Floor Level", options=floor_bin_options)#index=default_index)
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
        
        import plotly.graph_objects as go
        import pandas as pd
        import streamlit as st
        
        if final_df is not None:
            st.success("✅ Prediction Successful!")
        
            st.write("### Last 10 Months Forecast")
            st.dataframe(final_df.tail(10))
        
            # Prepare Data
            df_chart = final_df.copy()
            df_chart["month"] = pd.to_datetime(df_chart["month"], errors="coerce")
        
            # Create line chart
            fig = go.Figure()
        
            # Median price line
            fig.add_trace(go.Scatter(
                x=df_chart["month"],
                y=df_chart["median_price"],
                mode="lines+markers",
                name="Median Price",
                line=dict(color="blue"),
                marker=dict(size=6)
            ))
        
            # Add vertical line at Nov 2025
            nov_date = pd.Timestamp("2025-11-01")
            fig.add_vline(x=nov_date, line=dict(color="red", width=2, dash="dash"), annotation_text="Nov 2025", annotation_position="top right")
        
            fig.update_layout(
                title="Median Price Forecast",
                xaxis_title="Month",
                yaxis_title="Median Price",
                xaxis=dict(tickformat="%b %Y"),
                template="plotly_white"
            )
        
            st.plotly_chart(fig, use_container_width=True)

