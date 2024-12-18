import streamlit as st
st.write(st.secrets)  # This will display all secrets in the Streamlit app

credentials_json = json.loads(st.secrets["google"]["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
