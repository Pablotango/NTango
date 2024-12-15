
import streamlit as st
import pandas as pd
import datetime
import requests
import base64
import io


# GitHub repository details
GITHUB_REPO = "Pablotango/NTango"
GITHUB_FILE_PATH = "membership_applications.csv"
GITHUB_TOKEN = "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"  # Replace with your GitHub token


# Function to get the existing CSV data from GitHub
def get_existing_csv():
    try:
        # GitHub API endpoint for getting file contents
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
        
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            file_content = response.json()['content']
            file_content_decoded = base64.b64decode(file_content).decode('utf-8')
            # Load the CSV data into a DataFrame
            existing_data = pd.read_csv(io.StringIO(file_content_decoded))
            return existing_data
        else:
            # If file doesn't exist, return an empty DataFrame
            return pd.DataFrame(columns=["Timestamp", "Full Name", "Email", "Phone", "Address", "Payment Method", "Accepted Terms"])
    except Exception as e:
        st.error(f"Error fetching file from GitHub: {e}")
        return pd.DataFrame(columns=["Timestamp", "Full Name", "Email", "Phone", "Address", "Payment Method", "Accepted Terms"])

# Function to upload the CSV file to GitHub
def upload_to_github(data):
    try:
        # Convert the DataFrame to CSV and then to base64
        csv_data = data.to_csv(index=False)
        csv_encoded = base64.b64encode(csv_data.encode()).decode()
        
        # GitHub API endpoint for creating or updating a file
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
        
        # Get the current file's SHA (needed to update the file)
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        response = requests.get(url, headers=headers)
        
        # Prepare the payload for the API request
        if response.status_code == 200:
            file_sha = response.json()["sha"]
            commit_message = "Update membership applications"
        else:
            # If the file doesn't exist, we don't have a SHA
            file_sha = ""
            commit_message = "Create membership applications file"
        
        # Prepare the payload
        payload = {
            "message": commit_message,
            "content": csv_encoded,
            "sha": file_sha
        }
        
        # Send the request to GitHub
        response = requests.put(url, json=payload, headers=headers)
        
        # Check the response
        if response.status_code == 201 or response.status_code == 200:
            return True
        else:
            st.error(f"Failed to upload file to GitHub: {response.json().get('message')}")
            return False
    except Exception as e:
        st.error(f"Error: {e}")
        return False

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
    
    # Step 2: Payment options (both payment methods displayed)
    
    bank_details = "Account Name: Northern Tango Inc, BSB: 123-456, Account No: 987654321"
    square_link = "[Pay via Square](https://square.link/u/4CwZHhIS)"
    
    # Display both payment options always
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
        # Prepare data to save to the CSV
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        accepted_terms = "Yes" if agree_to_terms else "No"
        data_to_save = [[timestamp, full_name, email, phone, address, payment_method, accepted_terms]]
        
        # Convert the new data to a DataFrame
        new_data = pd.DataFrame(data_to_save, columns=["Timestamp", "Full Name", "Email", "Phone", "Address", "Payment Method", "Accepted Terms"])

        # Get existing data from GitHub
        existing_data = get_existing_csv()
        
        # Append the new data to the existing data
        updated_data = pd.concat([existing_data, new_data], ignore_index=True)

        # Upload the updated data directly to GitHub
        if upload_to_github(updated_data):
            st.success("Your application has been successfully submitted and the CSV has been updated on GitHub!")
            st.balloons()
        else:
            st.error("There was an error submitting your application. Please try again later.")
