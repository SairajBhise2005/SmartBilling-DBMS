import streamlit as st
import pandas as pd
from utils import get_services, add_service, update_service, delete_service

def show_services_page():
    st.title("🐕 Services Management")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["Add Service", "Service List"])
    
    with tab1:
        with st.form("add_service_form"):
            st.subheader("Add New Service")
            name = st.text_input("Service Name")
            description = st.text_area("Description (max 50 words)", max_chars=300)
            unit_price = st.number_input("Unit Price (Rs.)", min_value=0.0, step=0.01)
            
            submit_button = st.form_submit_button("Save Service")
            
            if submit_button:
                if not name:
                    st.error("Service Name is required!")
                elif unit_price <= 0:
                    st.error("Unit Price must be greater than Rs. 0!")
                else:
                    # Check if service with this name already exists
                    existing_services = get_services()
                    if existing_services and any(s['servicename'].lower() == name.lower() for s in existing_services):
                        st.error(f"A service with the name '{name}' already exists! Please use a different name.")
                    else:
                        service_data = {
                            "name": name,
                            "description": description,
                            "unit_price": unit_price
                        }
                        if add_service(service_data):
                            st.rerun()
    
    with tab2:
        st.subheader("Service List")
        services = get_services()
        
        if services:
            df = pd.DataFrame(services)
            # Rename columns for display
            df = df.rename(columns={
                'serviceid': 'ID',
                'servicename': 'Name',
                'description': 'Description',
                'unitprice': 'Unit Price',
                'createddate': 'Created Date'
            })
            # Format the unit price as currency
            if 'Unit Price' in df.columns:
                df['Unit Price'] = df['Unit Price'].apply(lambda x: f"Rs. {x:,.2f}")
            st.dataframe(df)
            
            # Edit/Delete functionality
            st.subheader("Manage Services")
            service_ids = [s['serviceid'] for s in services]
            selected_id = st.selectbox(
                "Select Service to Manage", 
                service_ids, 
                format_func=lambda x: f"{next(s['servicename'] for s in services if s['serviceid'] == x)} (Rs. {next(s['unitprice'] for s in services if s['serviceid'] == x):,.2f})"
            )
            
            if selected_id:
                selected_service = next(s for s in services if s['serviceid'] == selected_id)
                
                col1, col2 = st.columns(2)
                with col1:
                    with st.expander("Edit Service"):
                        with st.form("edit_service_form"):
                            edit_name = st.text_input("Name", value=selected_service['servicename'])
                            edit_description = st.text_area("Description", value=selected_service['description'])
                            edit_price = st.number_input("Unit Price", value=float(selected_service['unitprice']), min_value=0.0, step=0.01)
                            
                            update_button = st.form_submit_button("Update Service")
                            
                            if update_button:
                                if not edit_name:
                                    st.error("Service Name is required!")
                                elif edit_price <= 0:
                                    st.error("Unit Price must be greater than Rs. 0!")
                                else:
                                    updated_data = {
                                        "name": edit_name,
                                        "description": edit_description,
                                        "unit_price": edit_price
                                    }
                                    if update_service(selected_id, updated_data):
                                        st.rerun()
                
                with col2:
                    with st.expander("Delete Service"):
                        st.warning("This action cannot be undone")
                        if st.button("Delete Service"):
                            try:
                                if delete_service(selected_id):
                                    st.success("Service deleted successfully!")
                                    st.rerun()
                            except Exception as e:
                                if "invoiceservices" in str(e):
                                    st.error("Cannot delete this service as it is being used in one or more invoices. Please remove the service from all invoices first.")
                                else:
                                    st.error(f"Error deleting service: {str(e)}")
        else:
            st.info("No services found")