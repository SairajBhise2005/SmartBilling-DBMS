import streamlit as st
import os
import time
from supabase_config import supabase

def show_login_page():
    st.title("🐕 Smart Billing System")
    
    # Initialize session state
    if 'auth_status' not in st.session_state:
        st.session_state.auth_status = None
    
    tab1, tab2, tab3 = st.tabs(["Login", "Register", "Reset Password"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Login")
            
            if submit_button:
                try:
                    response = supabase.auth.sign_in_with_password({
                        "email": email,
                        "password": password
                    })
                    st.session_state.auth_status = True
                    st.success("Login successful!")
                    st.rerun()
                except Exception as e:
                    st.error("Invalid email or password")
    
    with tab2:
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name")
                phone = st.text_input("Phone Number")
                reg_email = st.text_input("Email")
            with col2:
                last_name = st.text_input("Last Name")
                reg_password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
            
            register_button = st.form_submit_button("Register")
            
            if register_button:
                if not all([first_name, last_name, phone, reg_email, reg_password]):
                    st.error("Please fill in all fields")
                elif reg_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    try:
                        # First create the auth user
                        auth_response = supabase.auth.sign_up({
                            "email": reg_email,
                            "password": reg_password
                        })
                        
                        # Then store additional user data
                        if auth_response.user:
                            user_data = {
                                "id": auth_response.user.id,
                                "first_name": first_name,
                                "last_name": last_name,
                                "email": reg_email,
                                "phone": phone,
                                "created_at": time.strftime('%Y-%m-%d %H:%M:%S')
                            }
                            
                            # Insert into users table
                            data_response = supabase.table('users').insert(user_data).execute()
                            
                            st.success("Registration successful! Please check your email to verify your account.")
                            time.sleep(2)
                            st.rerun()
                    except Exception as e:
                        st.error(f"Registration failed: {str(e)}")
                        # If user was created but data insertion failed, we should clean up
                        if 'auth_response' in locals() and auth_response.user:
                            try:
                                supabase.auth.admin.delete_user(auth_response.user.id)
                            except:
                                pass
    
    with tab3:
        with st.form("reset_password_form"):
            reset_email = st.text_input("Enter your email")
            reset_button = st.form_submit_button("Send Reset Link")
            
            if reset_button:
                try:
                    # Get the base URL for the app
                    base_url = os.getenv('STREAMLIT_SERVER_URL', 'http://localhost:8501')
                    
                    # Send password reset email
                    response = supabase.auth.reset_password_email(
                        reset_email,
                        options={
                            "redirect_to": f"{base_url}?type=recovery"
                        }
                    )
                    st.success("Password reset link has been sent to your email!")
                except Exception as e:
                    st.error(f"Error sending reset link: {str(e)}")

def handle_password_reset():
    """Handle password reset after clicking the email link"""
    st.title("Reset Password")
    
    try:
        # Get the token from the URL
        token = st.query_params.get("token") or st.query_params.get("access_token")
        
        if not token:
            st.error("Invalid or missing reset token")
            st.markdown("[← Back to Login](/?page=login)")
            return
            
        with st.form("new_password_form"):
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submit = st.form_submit_button("Reset Password")
            
            if submit:
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                    return
                    
                try:
                    # Update the user's password
                    response = supabase.auth.verify_otp({
                        "token": token,
                        "type": "recovery",
                        "new_password": new_password
                    })
                    
                    st.success("Password updated successfully!")
                    st.markdown("You can now [login](/) with your new password.")
                    
                    # Clear URL parameters
                    st.query_params.clear()
                    
                except Exception as e:
                    st.error(f"Error resetting password: {str(e)}")
                    if "expired" in str(e).lower():
                        st.info("The reset link has expired. Please request a new one.")
                        st.markdown("[← Request New Reset Link](/?page=login)")
    except Exception as e:
        st.error(f"Error processing reset request: {str(e)}")
        st.markdown("[← Back to Login](/?page=login)")

def init_auth():
    """Initialize authentication state"""
    try:
        user = supabase.auth.get_user()
        if user:
            st.session_state.auth_status = True
    except:
        st.session_state.auth_status = False 