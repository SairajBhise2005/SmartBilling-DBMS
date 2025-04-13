import streamlit as st
from utils import authenticate_user, register_user, send_password_reset

def show_login_page():
    st.title("🐕 SmartBilling - Dog Services")
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["Login", "Sign Up", "Forgot Password"])
    
    with tab1:
        with st.form("login_form"):
            st.subheader("Login to Your Account")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            login_button = st.form_submit_button("Login")
            
            if login_button:
                if authenticate_user(email, password):
                    st.session_state.logged_in = True
                    st.session_state.email = email
                    st.rerun()
                else:
                    st.error("Invalid email or password")
    
    with tab2:
        with st.form("signup_form"):
            st.subheader("Create New Account")
            st.markdown("""
            *About Paws & Care*  
            We're a premium dog service provider offering grooming, training, daycare, and veterinary services. 
            Our SmartBilling system helps you manage all your canine clients and their services efficiently.
            """)
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone Number")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            signup_button = st.form_submit_button("Sign Up")
            
            if signup_button:
                if password != confirm_password:
                    st.error("Passwords don't match")
                else:
                    if register_user(name, email, phone, password):
                        st.success("Account created successfully! Please login.")
                    else:
                        st.error("Email already registered")
    
    with tab3:
        with st.form("forgot_password_form"):
            st.subheader("Reset Your Password")
            email = st.text_input("Registered Email")
            reset_button = st.form_submit_button("Send Reset Link")
            
            if reset_button:
                if send_password_reset(email):
                    st.success("Password reset link sent to your email")
                else:
                    st.error("Email not found in our system")