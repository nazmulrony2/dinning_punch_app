import streamlit as st
import pandas as pd
import os

# Streamlit UI Configuration
st.title("Dining Punch Time Categorization App")
st.write("""
### Instructions:
1. **Upload a CSV File** with **5 columns**:  
   - `EmployeeID` (First column)  
   - `FirstName` (Second column)  
   - `Department` (Third column)  
   - `Date` (Fourth column, format: DD-MM-YYYY)  
   - `Time` (Fifth column)  
2. **The file should contain punch times**, and the app will categorize them into:  
   - **Dinner** (19:00 - 23:30)  
   - **Launch** (12:00 - 15:30)  
   - **Breakfast** (05:30 - 09:50)  
3. **Download the Processed CSV** after conversion.
""")

# File Upload Section
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    try:
        # Read CSV
        df = pd.read_csv(uploaded_file)

        # Ensure required columns exist
        required_columns = ["EmployeeID", "FirstName", "Department", "Date", "Time"]
        if not all(col in df.columns for col in required_columns):
            st.error("Uploaded file must have these columns: EmployeeID, FirstName, Department, Date, Time")
        else:
            # Try to infer any date format (flexible)
            df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors='coerce')
            df["Time"] = pd.to_datetime(df["Time"], format='%H:%M:%S', errors='coerce').dt.time

            # Drop rows with invalid date or time
            df.dropna(subset=["Date", "Time"], inplace=True)

            # Re-format date to DD-MM-YYYY for consistent display
            df["Date"] = df["Date"].dt.strftime('%d-%m-%Y')

            # Categorize times
            def categorize_time(time):
                if pd.to_datetime("19:00:00").time() <= time <= pd.to_datetime("23:30:00").time():
                    return "Dinner"
                elif pd.to_datetime("12:00:00").time() <= time <= pd.to_datetime("15:30:00").time():
                    return "Launch"
                elif pd.to_datetime("05:30:00").time() <= time <= pd.to_datetime("09:50:00").time():
                    return "Breakfast"
                return None

            df["Category"] = df["Time"].apply(categorize_time)
            df = df.dropna(subset=["Category"])

            # Pivot the table
            pivot_df = df.pivot_table(index=["EmployeeID", "FirstName", "Department", "Category"], 
                                      columns="Date", 
                                      values="Time", 
                                      aggfunc=lambda x: ', '.join(map(str, x)))

            # Reset index and clean format
            pivot_df.reset_index(inplace=True)
            pivot_df.columns.name = None

            # Display processed data
            st.write("### Processed Data:")
            st.dataframe(pivot_df)

            # Save and download
            output_filename = "Total_punches_dinning_flexible.csv"
            pivot_df.to_csv(output_filename, index=False)

            with open(output_filename, "rb") as file:
                st.download_button(label="Download Processed CSV", data=file, file_name=output_filename, mime="text/csv")

    except Exception as e:
        st.error(f"An error occurred: {e}")
