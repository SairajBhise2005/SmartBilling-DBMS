import streamlit as st

from supabase import create_client
from dotenv import load_dotenv
from Customers import customer_page
from signup import signup_page
import os

st.set_page_config(page_title="SmartBilling", layout="wide")

st.sidebar.title("📂 SmartBilling Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Customers", "Sign Up"])

if page == "Dashboard":
    st.title("📊 Dashboard")
    st.info("Dashboard is under construction.")

elif page == "Customers":
    customer_page()

elif page == "Sign Up":
    signup_page()
