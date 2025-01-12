import streamlit as st
import pandas as pd
import numpy as np

def process_data(df):
    # Extract unique dates from column B (assumes column B contains date-like values)
    unique_dates = df['B'].unique()
    unique_dates.sort()
    
    # Create an output DataFrame to store the processed data
    output = pd.DataFrame()
    output['Date'] = [unique_dates[i // 2] for i in range(len(unique_dates) * 2)]
    output['Exchange'] = 'ESX'
    output['Symbol'] = 'ETB'
    output['Market'] = 'Cash'
    output['Tenure'] = ['Overnight' if i % 2 == 0 else '7 Days' for i in range(len(unique_dates) * 2)]

    # Define calculations for each row in the output DataFrame
    open_prices, high_prices, low_prices, close_prices, wair_values, volumes, trades = [], [], [], [], [], [], []

    for i, row in output.iterrows():
        date = row['Date']
        tenure = row['Tenure']

        # Filter the input DataFrame for the current date and tenure
        filtered = df[(df['B'] == date) & (df['N'] == tenure)]

        # Open
        open_prices.append(filtered['L'].iloc[0] if not filtered.empty else 0)

        # High
        high_prices.append(filtered['L'].max() if not filtered.empty else 0)

        # Low
        low_prices.append(filtered['L'].min() if not filtered.empty else 0)

        # Close
        close_prices.append(filtered['L'].iloc[-1] if not filtered.empty else 0)

        # WAIR
        if not filtered.empty:
            wair = (filtered['J'] * filtered['L']).sum() / filtered['J'].sum()
            wair_values.append(wair)
        else:
            wair_values.append(0)

        # Volume
        volumes.append(filtered['J'].sum() / 2 if not filtered.empty else 0)

        # Trades
        trades.append(filtered['A'].nunique() if not filtered.empty else 0)

    # Add calculated columns to the output DataFrame
    output['Open'] = open_prices
    output['High'] = high_prices
    output['Low'] = low_prices
    output['Close'] = close_prices
    output['WAIR'] = wair_values
    output['Volume'] = volumes
    output['Trades'] = trades

    return output

# Streamlit App
st.title("Transaction Data Processor")

# File uploader
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    # Read the Excel file into a DataFrame
    df = pd.read_excel(uploaded_file, sheet_name='Full')

    # Ensure necessary columns exist
    required_columns = ['A', 'B', 'J', 'L', 'N']
    if all(col in df.columns for col in required_columns):
        # Process the data
        processed_data = process_data(df)

        # Display the processed data
        st.write("Processed Data:")
        st.dataframe(processed_data)

        # Allow download of the processed data
        output_file = processed_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Processed Data",
            data=output_file,
            file_name="processed_data.csv",
            mime="text/csv"
        )
    else:
        st.error(f"The uploaded file must contain the following columns: {', '.join(required_columns)}")
