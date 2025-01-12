import streamlit as st
import pandas as pd
import numpy as np

# Load the Excel file
data_file = 'Full.xlsx'
data = pd.read_excel(data_file, sheet_name='Full')

# Process the data
def process_data(data):
    # Extract unique dates
    unique_dates = data['B'].drop_duplicates().reset_index(drop=True)

    # Prepare the DataFrame for the output
    output = pd.DataFrame()
    output['Date'] = np.repeat(unique_dates, 2).reset_index(drop=True)
    output['Exchange'] = 'ESX'
    output['Symbol'] = 'ETB'
    output['Market'] = 'Cash'
    output['Tenure'] = ['Overnight' if i % 2 == 0 else '7 Days' for i in range(len(output))]

    # Calculate Open, High, Low, Close, WAIR, Volume, and Trades
    open_prices, high_prices, low_prices, close_prices, wair_values, volumes, trades = [], [], [], [], [], [], []

    for i, row in output.iterrows():
        date = row['Date']
        tenure = row['Tenure']

        # Filter the data for the specific date and tenure
        filtered = data[(data['B'] == date) & (data['N'] == tenure)]

        if not filtered.empty:
            open_prices.append(filtered.iloc[0]['L'])
            high_prices.append(filtered['L'].max())
            low_prices.append(filtered['L'].min())
            close_prices.append(filtered['L'].iloc[-1])

            wair = (filtered['J'] * filtered['L']).sum() / filtered['J'].sum()
            wair_values.append(wair)

            volumes.append(filtered['J'].sum() / 2)
            trades.append(filtered['A'].nunique())
        else:
            open_prices.append(0)
            high_prices.append(0)
            low_prices.append(0)
            close_prices.append(0)
            wair_values.append(0)
            volumes.append(0)
            trades.append(0)

    output['Open'] = open_prices
    output['High'] = high_prices
    output['Low'] = low_prices
    output['Close'] = close_prices
    output['WAIR'] = wair_values
    output['Volume'] = volumes
    output['Trades'] = trades

    return output

# Process the data
output_data = process_data(data)

# Streamlit app
st.title('Transaction Data Processing')
st.write("Processed Data")
st.dataframe(output_data)

# Download button for the processed data
@st.cache
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df(output_data)
st.download_button(
    label="Download Processed Data",
    data=csv,
    file_name='processed_data.csv',
    mime='text/csv',
)
