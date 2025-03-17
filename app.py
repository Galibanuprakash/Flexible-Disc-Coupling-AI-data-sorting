import streamlit as st
import pandas as pd
import google.generativeai as genai

# Configure Google Gemini API
GEMINI_API_KEY = "AIzaSyCFbnID7J4KnD-hoveRc37CEx_MV9eXUEk"
genai.configure(api_key=GEMINI_API_KEY)

# Load Excel data
@st.cache_data
def load_data(uploaded_file):
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file, sheet_name="Main-Data")
        df.columns = df.iloc[0]  # Set first row as column headers
        df = df[1:].reset_index(drop=True)  # Cleaned data
        
        # Convert numeric columns safely, replacing invalid values with NaN
        numeric_cols = ["Speed (RPM)", "Power (kW)"]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        
        return df.dropna(subset=numeric_cols)  # Drop rows with NaN in essential columns
    return None

# Streamlit UI
st.title("Flexible Disc Coupling Finder")

# File Upload
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
if uploaded_file:
    df = load_data(uploaded_file)
    st.success("File uploaded successfully!")
else:
    df = None
    st.warning("Please upload an Excel file to proceed.")

# User Inputs
coupling_model = st.text_input("Enter Coupling Model")
speed = st.number_input("Enter Required Speed (RPM)", min_value=0, step=10)
power = st.number_input("Enter Required Power (kW)", min_value=0.0, step=0.1)
shaft_dia = st.number_input("Enter Shaft Diameter (mm)", min_value=0.0, step=0.1)
pcd_1 = st.number_input("Enter PCD-1", min_value=0.0, step=0.1)

if st.button("Find Best Coupling") and df is not None:
    # Apply filtering based on user input
    df_filtered = df[(df["Speed (RPM)"] >= speed) &
                     (df["Power (kW)"] >= power)]
    
    if not df_filtered.empty:
        best_match = df_filtered.iloc[0]  # Selecting the best match
        st.success(f"Best Matching Coupling: {best_match['Coupling \nModel']}")
        st.write(best_match.to_dict())
        
        # Use Google Gemini API for recommendations
        prompt = f"Suggest a flexible disc coupling for model {coupling_model}, {speed} RPM speed, {power} kW power, {shaft_dia} mm shaft diameter, and {pcd_1} PCD-1."
        response = genai.GenerativeModel("gemini-pro").generate_content(prompt)
        st.subheader("Gemini AI Recommendation:")
        st.write(response.text)
    else:
        st.error("No suitable coupling found. Try adjusting the parameters.")
