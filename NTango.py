
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Pablo_offline/py/NTango/ntangp-membership-f980ceb098ec.json"

import streamlit as st
import datetime
from google.cloud import firestore

# Initialize Firestore client
db = firestore.Client()

# Reference to the Firestore collection
collection_ref = db.collection('membership_applications')

# Streamlit app
st.title("Northern Tango Inc - Membership Application")

st.write("Welcome! Please fill out the form below to apply for membership.")

# Step 1: Collect membership details inside the form
with st.form("membership_form"):
    st.header("1. Membership Details")
    full_name = st.text_input("Full Name", max_chars=50)
    email = st.text_input("Email Address")
    phone = st.text_input("Phone Number")
    address = st.text_area("Address")

    # Step 2: Payment options with radio buttons (user must choose one)
    st.header("2. Payment Options")
    payment_method = st.radio("Select Payment Method", ["Bank Transfer", "Square Link"])
    
    # Display payment options
    bank_details = "Account Name: Northern Tango Inc, BSB: 123-456, Account No: 987654321"
    square_link = "[Pay via Square](https://square.link/u/4CwZHhIS)"
    st.subheader("Bank Transfer")
    st.info(f"Please use the following bank details for your payment:\n\n{bank_details}")
    
    st.subheader("Square Link")
    st.markdown(f"Click here to pay: {square_link}")

    # Step 3: Accept terms and conditions
    st.header("3. Accept Terms")
    agree_to_terms = st.checkbox("I agree to the terms and conditions")

    # Step 4: Submit button (submit happens at the bottom)
    submit = st.form_submit_button("Submit Application")

# Handle form submission
if submit:
    # Step 5: Handle form submission
    if not (full_name and email and phone and address and agree_to_terms):
        st.error("Please complete all fields and agree to the terms and conditions.")
    else:
        # Prepare data to save to Firestore
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        accepted_terms = "Yes" if agree_to_terms else "No"
        
        # Prepare data as a dictionary
        data_to_save = {
            'timestamp': timestamp,
            'full_name': full_name,
            'email': email,
            'phone': phone,
            'address': address,
            'payment_method': payment_method,
            'accepted_terms': accepted_terms
        }

        try:
            # Save the data to Firestore
            collection_ref.add(data_to_save)

            st.success("Your application has been successfully submitted and stored in Firestore!")
            st.balloons()

        except Exception as e:
            st.error(f"Error submitting your application: {e}")
