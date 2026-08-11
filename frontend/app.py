import streamlit as st
import pandas as pd
import requests

# Base URL of the Flask backend (Docker container name on shared network)
BACKEND_URL = "http://backend:7860"

# Page configuration
st.set_page_config(page_title="SuperKart Sales Prediction", page_icon="🛒", layout="wide")

# Title
st.title("🛒 SuperKart Sales Prediction App")
st.write("Enter product and store details below to predict the sales revenue.")

st.divider()

# --- Single Prediction ---
st.subheader("Single Product-Store Sales Prediction")

col1, col2 = st.columns(2)

with col1:
    Product_Weight = st.number_input("Product Weight (kg)", min_value=4.0, max_value=22.0, value=12.5, step=0.1)
    
    Product_Sugar_Content = st.selectbox(
        "Product Sugar Content",
        ["Low Sugar", "Regular", "No Sugar"]
    )
    
    Product_Allocated_Area = st.number_input(
        "Product Allocated Area (ratio)", min_value=0.004, max_value=0.300, value=0.07, step=0.001, format="%.3f"
    )
    
    Product_Type = st.selectbox(
        "Product Type",
        ["Frozen Foods", "Dairy", "Canned", "Baking Goods", "Health and Hygiene",
         "Snack Foods", "Meat", "Household", "Hard Drinks", "Fruits and Vegetables",
         "Breads", "Soft Drinks", "Breakfast", "Others", "Starchy Foods", "Seafood"]
    )
    
    Product_MRP = st.number_input("Product MRP", min_value=31.0, max_value=266.0, value=147.0, step=1.0)

with col2:
    Store_Size = st.selectbox("Store Size", ["Small", "Medium", "High"])
    
    Store_Location_City_Type = st.selectbox(
        "Store Location City Type",
        ["Tier 1", "Tier 2", "Tier 3"]
    )
    
    Store_Type = st.selectbox(
        "Store Type",
        ["Supermarket Type1", "Supermarket Type2", "Departmental Store", "Food Mart"]
    )
    
    Store_Age = st.number_input("Store Age (years)", min_value=1, max_value=50, value=17, step=1)

# Create JSON payload
product_data = {
    "Product_Weight": Product_Weight,
    "Product_Sugar_Content": Product_Sugar_Content,
    "Product_Allocated_Area": Product_Allocated_Area,
    "Product_Type": Product_Type,
    "Product_MRP": Product_MRP,
    "Store_Size": Store_Size,
    "Store_Location_City_Type": Store_Location_City_Type,
    "Store_Type": Store_Type,
    "Store_Age": Store_Age
}

# Predict button
if st.button("Predict Sales", type="primary"):
    try:
        response = requests.post(f"{BACKEND_URL}/v1/predict", json=product_data)
        if response.status_code == 200:
            result = response.json()
            predicted_sales = result["Predicted_Sales"]
            st.success(f"💰 Predicted Sales Revenue: ₹ {predicted_sales:,.2f}")
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
    except requests.exceptions.ConnectionError:
        st.error("Unable to connect to the prediction API. Ensure the backend is running.")

st.divider()

# --- Batch Prediction ---
st.subheader("Batch Prediction")
st.write("Upload a CSV file with product-store data to get predictions for multiple records.")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:
    if st.button("Predict for Batch", type="primary"):
        try:
            response = requests.post(
                f"{BACKEND_URL}/v1/predict_batch",
                files={"file": uploaded_file}
            )
            if response.status_code == 200:
                results = response.json()
                st.success("Predictions completed successfully!")
                
                if isinstance(results, dict):
                    if 'predictions' in results:
                        df_results = pd.DataFrame({'Predicted_Sales': results['predictions']})
                    else:
                        df_results = pd.DataFrame(list(results.items()), columns=['Product_Id', 'Predicted_Sales'])
                else:
                    df_results = pd.DataFrame(results)
                
                st.dataframe(df_results, use_container_width=True)
                
                # Download button for results
                csv_output = df_results.to_csv(index=False).encode('utf-8')
                st.download_button("Download Predictions CSV", csv_output, "predictions.csv", "text/csv")
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
        except requests.exceptions.ConnectionError:
            st.error("Unable to connect to the prediction API. Ensure the backend is running.")
