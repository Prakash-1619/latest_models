import streamlit as st
import pandas as pd
import numpy as np
from model_testing1 import predict_with_area  # replace file name

# ---------------------------------------------------
# LOAD RANGE FILE
# ---------------------------------------------------
range_df = pd.read_csv("column_input_ranges.csv")

# AREA LIST
area_list = range_df["area_name_en"].tolist()

# LOAD DASH DATA
data_for_dash = pd.read_csv("Data_data_columns/data_for_dash.csv")
data_for_dash['instance_date'] = pd.to_datetime(data_for_dash['instance_date'], errors='coerce')
data_for_dash['month'] = data_for_dash['instance_date'].dt.to_period('M')

 
# YES/NO → 1/0
to_bool = lambda x: 1 if x == "Yes" else 0

# ---------------------------------------------------
# STREAMLIT UI
# ---------------------------------------------------
st.title("Dubai Real Estate Dashboard")

tab1, tab2 = st.tabs(["Prediction", "Monthly Trend"])

# ----------------- TAB 1 -----------------
with tab1:
    st.header("Property Price Prediction")

    # Step 1 — Area Selection
    area = st.selectbox("Select Area", ["-- Select Area --"] + area_list)

    if area != "-- Select Area --":
        st.subheader(f"Enter Property Features for **{area}**")
        row = range_df[range_df["area_name_en"] == area].iloc[0]

        median_area = float(row["median_procedure_area"])
        min_area    = float(row["min"])
        max_area    = float(row["max"])

        procedure_area = st.number_input(
            "Procedure Area (sq.m)",
            min_value=min_area,
            max_value=max_area,
            value=median_area
        )

        rooms_options = ['1 B/R', 'Studio', '2 B/R', '3 B/R', 'PENTHOUSE', 'More than 3B/R']
        floor_bin_options = ['1-10', '11-20', '41-50', '21-30', 'Below 1st floor', '31-40',
                             '51-60', 'Other', '-9-0', '61-70', 'Top floor', '91-100', '81-90',
                             '71-80', 'Duplex']

        rooms_en = st.selectbox("Number of Rooms", options=rooms_options)
        floor_bin = st.selectbox("Floor Level", options=floor_bin_options)
        has_parking   = to_bool(st.selectbox("Parking", ["Yes", "No"]))
        swimming_pool = to_bool(st.selectbox("Swimming Pool", ["Yes", "No"]))
        balcony       = to_bool(st.selectbox("Balcony", ["Yes", "No"]))
        elevator      = to_bool(st.selectbox("Elevator", ["Yes", "No"]))
        metro         = to_bool(st.selectbox("Metro Access", ["Yes", "No"]))

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
                st.write("### Last 10 Months Forecast")
                st.dataframe(final_df.tail(10))
                df_chart = final_df.copy()
                df_chart["month"] = pd.to_datetime(df_chart["month"], errors="coerce")
                st.line_chart(df_chart.set_index("month")["median_price"])

# ----------------- TAB 2 -----------------
with tab2:
    st.header("Monthly Trend + Forecast")

    # Feature selection
    sel_area = st.selectbox("Select Area", ["-- Select Area --"] + area_list, key="trend_area")
    sel_rooms = st.selectbox("Select Rooms", ['1 B/R', 'Studio', '2 B/R', '3 B/R', 'PENTHOUSE', 'More than 3B/R'], key="trend_rooms")
    sel_floor = st.selectbox("Select Floor Bin", ['1-10', '11-20', '41-50', '21-30', 'Below 1st floor', '31-40',
                                                  '51-60', 'Other', '-9-0', '61-70', 'Top floor', '91-100', '81-90',
                                                  '71-80', 'Duplex'], key="trend_floor")
    sel_parking   = st.selectbox("Parking", ["Yes", "No"], key="trend_parking")
    sel_pool      = st.selectbox("Swimming Pool", ["Yes", "No"], key="trend_pool")
    sel_balcony   = st.selectbox("Balcony", ["Yes", "No"], key="trend_balcony")
    sel_elevator  = st.selectbox("Elevator", ["Yes", "No"], key="trend_elevator")
    sel_metro     = st.selectbox("Metro Access", ["Yes", "No"], key="trend_metro")

    if st.button("Show Trend + Forecast"):
        # -------------------------
        # Filter historical data
        # -------------------------
        trend_df = data_for_dash[
            (data_for_dash["area_name_en"] == sel_area) &
            (data_for_dash["rooms_en"] == sel_rooms) &
            (data_for_dash["floor_bin"] == sel_floor) &
            (data_for_dash["has_parking"] == to_bool(sel_parking)) &
            (data_for_dash["swimming_pool"] == to_bool(sel_pool)) &
            (data_for_dash["balcony"] == to_bool(sel_balcony)) &
            (data_for_dash["elevator"] == to_bool(sel_elevator)) &
            (data_for_dash["metro"] == to_bool(sel_metro))
        ].copy()

        if trend_df.empty:
            st.warning("No historical data found for selected features!")
        else:
            # Convert date to month start
            trend_df['month'] = pd.to_datetime(trend_df['instance_date'], errors='coerce')
            trend_df = trend_df.set_index('month').resample('MS').median(numeric_only=True)
            trend_df.rename(columns={'meter_sale_price': 'median_price'}, inplace=True)
            trend_df['median_price'] = trend_df['median_price'].interpolate().bfill()
            trend_df = trend_df.reset_index()

            # -------------------------
            # Predict next value using model
            # -------------------------
            input_data = {
                "area_name_en": sel_area,
                "procedure_area": trend_df['median_price'].median(),  # use median as proxy
                "has_parking": to_bool(sel_parking),
                "floor_bin": sel_floor,
                "rooms_en": sel_rooms,
                "swimming_pool": to_bool(sel_pool),
                "balcony": to_bool(sel_balcony),
                "elevator": to_bool(sel_elevator),
                "metro": to_bool(sel_metro)
            }

            forecast_df = predict_with_area(input_data)  # same as Tab1
            # Optionally apply growth factor to forecast months
            growth_factor = 1.02  # 2% growth per month, adjust as needed
            forecast_df['median_price'] = forecast_df['median_price'] * growth_factor

            # -------------------------
            # Combine historical + forecast
            # -------------------------
            combined_df = pd.concat([trend_df, forecast_df], ignore_index=True, sort=False)

            # -------------------------
            # Display
            # -------------------------
            st.write("### Historical + Forecast")
            st.dataframe(combined_df)
            combined_df['month_dt'] = pd.to_datetime(combined_df['month'])
            st.line_chart(combined_df.set_index('month_dt')['median_price'])
