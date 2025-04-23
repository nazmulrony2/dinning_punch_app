import streamlit as st
import pandas as pd
import os

# Streamlit UI Configuration
st.title("Dining Punch Time Categorization App")
st.write("""
### Instructions:
1. **Upload a CSV File** with **5 columns**:  
   - `EmployeeID` (First column)  
   - `Name` (Second column)  
   - `Department` (Third column)  
   - `Date` (Fourth column, format: DD-MM-YYYY)  
   - `Time` (Fifth column)  
2. **The file should contain punch times**, and the app will categorize them into:  
   - **Dinner** (19:00 - 23:00)  
   - **Launch** (12:00 - 15:00)  
   - **Breakfast** (06:00 - 09:00)  
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
            st.error("Uploaded file must have these columns: EmployeeID, Name, Department, Date, Time")
        else:
            # Convert Date and Time columns
            df["Date"] = pd.to_datetime(df["Date"], format='%d-%m-%Y').dt.strftime('%d-%m-%Y')  # Format to DD-MM-YYYY
            df["Time"] = pd.to_datetime(df["Time"], format='%H:%M:%S').dt.time

            # Define time segments
            def categorize_time(time):
                if pd.to_datetime("19:00:00").time() <= time <= pd.to_datetime("23:30:00").time():
                    return "Dinner"
                elif pd.to_datetime("12:00:00").time() <= time <= pd.to_datetime("15:30:00").time():
                    return "Launch"
                elif pd.to_datetime("05:30:00").time() <= time <= pd.to_datetime("09:50:00").time():
                    return "Breakfast"
                return None

            # Apply category function
            df["Category"] = df["Time"].apply(categorize_time)
            df = df.dropna(subset=["Category"])

            # Pivot the table
            pivot_df = df.pivot_table(index=["EmployeeID", "Name", "Department", "Category"], 
                                    columns="Date", 
                                    values="Time", 
                                    aggfunc=lambda x: ', '.join(map(str, x)))

            # Reset index and clean format
            pivot_df.reset_index(inplace=True)
            pivot_df.columns.name = None  # Remove 'Date' label from columns

            # Display dataframe
            st.write("### Processed Data:")
            st.dataframe(pivot_df)

            # Save and download
            output_filename = "Total_punches_dinning1-6.csv"
            pivot_df.to_csv(output_filename, index=False)
            
            with open(output_filename, "rb") as file:
                st.download_button(label="Download Processed CSV", data=file, file_name=output_filename, mime="text/csv")

    except Exception as e:
        st.error(f"An error occurred: {e}")
