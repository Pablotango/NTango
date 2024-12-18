import os
import streamlit as st
import datetime
from google.cloud import firestore
import json
import tempfile

# Replace escaped newline characters in the private key
credentials_json["private_key"] = credentials_json["private_key"].replace("\\n", "\n")

# Read the credentials JSON from Streamlit secrets
credentials_json = st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"]

# Create a temporary file to store the modified credentials JSON
with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
    json.dump(credentials_json, temp_file, indent=4)  # Save the JSON to the temporary file
    temp_credentials_path = temp_file.name
    
# Set the GOOGLE_APPLICATION_CREDENTIALS environment variable
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_credentials_path

# Initialize Firestore client
db = firestore.Client(database="ntangomembership1")

# Reference Firestore collection
collection_ref = db.collection('membership_applications')

# Streamlit app
st.title("Northern Tango Inc - Membership Application")
st.write("Welcome! Please fill out the form below to apply for membership.")

# Membership form
with st.form("membership_form"):
    st.header("1. Membership Details")
    full_name = st.text_input("Full Name", max_chars=50)
    email = st.text_input("Email Address")
    phone = st.text_input("Phone Number")
    address = st.text_area("Address")

    # Payment options
    st.header("2. Payment Options")
    payment_method = st.radio("Select Payment Method", ["Bank Transfer", "Square Link"])

    bank_details = "Account Name: Northern Tango Inc, BSB: 123-456, Account No: 987654321"
    square_link = "[Pay via Square](https://square.link/u/4CwZHhIS)"
    st.subheader("Bank Transfer")
    st.info(bank_details)
    st.subheader("Square Link")
    st.markdown(square_link)

    # Terms and conditions
    st.header("3. Accept Terms")
    agree_to_terms = st.checkbox("I agree to the terms and conditions")

    submit = st.form_submit_button("Submit Application")

# Handle form submission
if submit:
    if not (full_name and email and phone and address and agree_to_terms):
        st.error("Please complete all fields and agree to the terms and conditions.")
    else:
        # Prepare data for Firestore
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data_to_save = {
            'timestamp': timestamp,
            'full_name': full_name,
            'email': email,
            'phone': phone,
            'address': address,
            'payment_method': payment_method,
            'accepted_terms': "Yes" if agree_to_terms else "No"
        }

        try:
            # Add data to Firestore
            collection_ref.add(data_to_save)
            st.success("Your application has been successfully submitted!")
            st.balloons()
        except Exception as e:
            import traceback
            st.error(f"Error submitting your application: {e}")
            st.text(traceback.format_exc())
