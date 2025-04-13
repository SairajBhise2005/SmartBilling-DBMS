import streamlit as st
import pandas as pd
from utils import get_customers, add_customer, update_customer, delete_customer, get_customer_history

def show_customers_page():
    st.title("🐕 Customer Management")
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["Add Customer", "Customer List", "Customer History"])
    
    with tab1:
        with st.form("add_customer_form"):
            st.subheader("Add New Customer")
            name = st.text_input("Customer Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone Number")
            address = st.text_area("Address")
            
            submit_button = st.form_submit_button("Save Customer")
            
            if submit_button:
                if not name:
                    st.error("Customer Name is required!")
                elif not email:
                    st.error("Email is required!")
                else:
                    # Check if customer with this email already exists
                    existing_customers = get_customers()
                    if existing_customers and any(c['email'] == email for c in existing_customers) and any(c['phonenumber'] == phone for c in existing_customers):
                        st.error("Customer already exists! Please use a different email or phone number.")
                    else:
                        # Only try to add customer if they don't already exist
                        customer_data = {
                            'name': name,
                            'email': email,
                            'phone': phone,
                            'address': address
                        }
                        success = add_customer(customer_data)
                        if success:
                            st.success("Customer added successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to add customer. Please try again.")
    
    with tab2:
        st.subheader("Customer List")
        customers = get_customers()
        
        if customers:
            df = pd.DataFrame(customers)
            st.dataframe(df.rename(columns={
                'customerid': 'ID',
                'customername': 'Name',
                'email': 'Email',
                'phonenumber': 'Phone',
                'address': 'Address',
                'createddate': 'Created Date'
            }))
            
            # Edit/Delete functionality
            st.subheader("Manage Customers")
            customer_ids = [c['customerid'] for c in customers]
            selected_id = st.selectbox(
                "Select Customer to Manage", 
                customer_ids, 
                format_func=lambda x: f"{next(c['customername'] for c in customers if c['customerid'] == x)} (ID: {x})"
            )
            
            if selected_id:
                selected_customer = next(c for c in customers if c['customerid'] == selected_id)
                
                col1, col2 = st.columns(2)
                with col1:
                    with st.expander("Edit Customer"):
                        with st.form("edit_customer_form"):
                            edit_name = st.text_input("Name", value=selected_customer['customername'])
                            edit_email = st.text_input("Email", value=selected_customer['email'])
                            edit_phone = st.text_input("Phone", value=selected_customer['phonenumber'])
                            edit_address = st.text_area("Address", value=selected_customer['address'])
                            
                            update_button = st.form_submit_button("Update Customer")
                            
                            if update_button:
                                updated_data = {
                                    "name": edit_name,
                                    "email": edit_email,
                                    "phone": edit_phone,
                                    "address": edit_address
                                }
                                if update_customer(selected_id, updated_data):
                                    st.success("Customer updated successfully!")
                                    st.rerun()
                
                with col2:
                    with st.expander("Delete Customer"):
                        st.warning("This action cannot be undone")
                        if st.button("Delete Customer"):
                            if delete_customer(selected_id):
                                st.success("Customer deleted successfully!")
                                st.rerun()
        else:
            st.info("No customers found")
    
    with tab3:
        st.subheader("Customer History")
        customers = get_customers()
        
        if customers:
            customer_id = st.selectbox(
                "Select Customer", 
                [c['customerid'] for c in customers], 
                format_func=lambda x: f"{next(c['customername'] for c in customers if c['customerid'] == x)} (ID: {x})"
            )
            
            history = get_customer_history(customer_id)
            
            if history['customer']:
                st.markdown(f"### History for {history['customer']['customername']}")
                
                st.markdown("#### Invoices")
                if history['invoices']:
                    df_invoices = pd.DataFrame(history['invoices'])
                    # Rename columns for better display
                    df_invoices = df_invoices.rename(columns={
                        'invoiceid': 'Invoice ID',
                        'customerid': 'Customer ID',
                        'invoicedate': 'Date',
                        'duedate': 'Due Date',
                        'totalamount': 'Total Amount',
                        'status': 'Status'
                    })
                    st.dataframe(df_invoices)
                else:
                    st.info("No invoices found")
                
                st.markdown("#### Payments")
                if history['payments']:
                    df_payments = pd.DataFrame(history['payments'])
                    # Rename columns for better display
                    df_payments = df_payments.rename(columns={
                        'paymentid': 'Payment ID',
                        'invoiceid': 'Invoice ID',
                        'paymentdate': 'Payment Date',
                        'paymentmethod': 'Method',
                        'amountpaid': 'Amount'
                    })
                    # Format the payment date
                    if 'Payment Date' in df_payments.columns:
                        df_payments['Payment Date'] = pd.to_datetime(df_payments['Payment Date']).dt.strftime('%Y-%m-%d %H:%M')
                    # Format the amount with 2 decimal places
                    if 'Amount' in df_payments.columns:
                        df_payments['Amount'] = df_payments['Amount'].apply(lambda x: f"Rs.{x:,.2f}")
                    st.dataframe(df_payments)
                else:
                    st.info("No payments found")
            else:
                st.info("No history found for this customer")
        else:
            st.info("No customers available")