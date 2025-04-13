import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from utils import get_customers, get_invoices, get_payments

def show_dashboard_page():
    st.title("🐕 Dashboard Overview")
    st.markdown("---")
    
    # Get data
    customers = get_customers()
    invoices = get_invoices()
    payments = get_payments()
    
    # Calculate metrics with error handling
    total_customers = len(customers) if customers else 0
    pending_invoices = len([inv for inv in invoices if inv.get('status', '') == 'unpaid']) if invoices else 0
    total_revenue = sum(float(p.get('amount', 0)) for p in payments) if payments else 0
    
    # Create cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="card">
            <h3>Total Customers</h3>
            <h1>{total_customers}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="card">
            <h3>Pending Invoices</h3>
            <h1>{pending_invoices}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="card">
            <h3>Total Revenue</h3>
            <h1>${total_revenue:,.2f}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recent activities with proper error handling
    st.subheader("Recent Activities")
    
    # Recent invoices
    if invoices:
        recent_invoices = sorted(invoices, key=lambda x: x.get('date', ''), reverse=True)[:5]
        st.markdown("*Recent Invoices*")
        
        # Create DataFrame with only available columns
        invoice_data = []
        for inv in recent_invoices:
            invoice_data.append({
                'invoice_id': inv.get('invoice_id', 'N/A'),
                'customer_name': inv.get('customer_name', 'Unknown'),
                'date': inv.get('date', 'N/A'),
                'status': inv.get('status', 'N/A'),
                'grand_total': inv.get('grand_total', 0)
            })
        
        df_invoices = pd.DataFrame(invoice_data)
        st.dataframe(df_invoices)
    else:
        st.info("No invoices available")
    
    # Recent payments
    if payments:
        recent_payments = sorted(payments, key=lambda x: x.get('date', ''), reverse=True)[:5]
        st.markdown("*Recent Payments*")
        
        # Create DataFrame with only available columns
        payment_data = []
        for p in recent_payments:
            payment_data.append({
                'payment_id': p.get('payment_id', 'N/A'),
                'invoice_id': p.get('invoice_id', 'N/A'),
                'date': p.get('date', 'N/A'),
                'method': p.get('method', 'N/A'),
                'amount': p.get('amount', 0)
            })
        
        df_payments = pd.DataFrame(payment_data)
        st.dataframe(df_payments)
    else:
        st.info("No payments available")
    
    # Quick charts (only show if data exists)
    if invoices and payments:
        st.markdown("---")
        st.subheader("Quick Insights")
        
        col1, col2 = st.columns(2)
        with col1:
            try:
                # Revenue by week
                payments_df = pd.DataFrame(payments)
                payments_df['date'] = pd.to_datetime(payments_df['date'])
                payments_df['week'] = payments_df['date'].dt.strftime('%Y-%U')
                weekly_revenue = payments_df.groupby('week')['amount'].sum().reset_index()
                fig = px.line(weekly_revenue, x='week', y='amount', title='Weekly Revenue')
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Could not generate revenue chart: {str(e)}")
        
        with col2:
            try:
                # Invoice status
                invoices_df = pd.DataFrame(invoices)
                status_counts = invoices_df['status'].value_counts().reset_index()
                fig = px.pie(status_counts, values='count', names='status', title='Invoice Status')
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Could not generate status chart: {str(e)}")

def show_dashboard():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("", ["Dashboard", "Customers", "Services", "Invoices", "Payments", "Reports", "Logout"])
    
    if page == "Logout":
        st.session_state.logged_in = False
        st.rerun()
    elif page == "Customers":
        from customers import show_customers_page
        show_customers_page()
    elif page == "Services":
        from services import show_services_page
        show_services_page()
    elif page == "Invoices":
        from invoices import show_invoices_page
        show_invoices_page()
    elif page == "Payments":
        from payments import show_payments_page
        show_payments_page()
    elif page == "Reports":
        from reports import show_reports_page
        show_reports_page()
    else:
        show_dashboard_page()