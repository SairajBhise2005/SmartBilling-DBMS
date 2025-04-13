# Import standard libraries first
import os
from dotenv import load_dotenv

# Import Streamlit and set page config before any other Streamlit commands
import streamlit as st
st.set_page_config(
    page_title="Smart Billing System",
    page_icon="🐕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import other dependencies after page config
from supabase import create_client, Client
from auth import show_login_page, init_auth, handle_password_reset
from dashboard import show_dashboard

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def main():
    # Check for password reset
    if st.query_params.get("type") == "recovery":
        handle_password_reset()
        return

    # Initialize authentication
    init_auth()
    
    # Show appropriate page based on auth status
    if not st.session_state.get('auth_status'):
        show_login_page()
    else:
        show_dashboard()

if __name__ == "__main__":
    main()