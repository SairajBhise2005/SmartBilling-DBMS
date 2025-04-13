import streamlit as st
import pandas as pd
from datetime import datetime
from utils import get_customers, get_unpaid_invoices, log_payment, get_payments

def show_payments_page():
    st.title("🐕 Payment Management")
    st.markdown("---")
    
    # Initialize session state for payment logging
    if 'payment_logged' not in st.session_state:
        st.session_state.payment_logged = False
    
    # Fetch customers data outside the tabs so it's available everywhere
    customers = get_customers()
    if not customers:
        st.error("No customers available")
        return
    
    tab1, tab2 = st.tabs(["Log Payment", "Payment History"])
    
    with tab1:
        st.subheader("Log New Payment")
            
        customer_id = st.selectbox(
            "Select Customer",
            [c['customerid'] for c in customers],
            format_func=lambda x: f"{next(c['customername'] for c in customers if c['customerid'] == x)}"
        )
        
        # Get customer's unpaid invoices
        unpaid_invoices = get_unpaid_invoices(customer_id)
        
        if not unpaid_invoices:
            st.warning("No unpaid invoices for this customer")
            return
            
        with st.form("log_payment_form"):
            invoice_id = st.selectbox(
                "Select Invoice",
                [inv['invoiceid'] for inv in unpaid_invoices],
                format_func=lambda x: f"Invoice #{x} (Rs. {next(inv['grandtotal'] for inv in unpaid_invoices if inv['invoiceid'] == x):.2f})"
            )
            
            selected_invoice = next(inv for inv in unpaid_invoices if inv['invoiceid'] == invoice_id)
            
            payment_method = st.selectbox(
                "Payment Method",
                ["Cash", "Card", "Online"]
            )
            
            payment_date = st.date_input("Payment Date", datetime.now())
            amount = st.number_input(
                "Amount",
                min_value=0.01,
                max_value=float(selected_invoice['grandtotal']),
                value=float(selected_invoice['grandtotal']),
                step=0.01
            )
            
            submit_button = st.form_submit_button("Log Payment")
            
            if submit_button:
                payment_data = {
                    "invoice_id": invoice_id,
                    "date": payment_date.strftime("%Y-%m-%d"),
                    "method": payment_method,
                    "amount": amount
                }
                
                payment_id = log_payment(payment_data)
                if payment_id:
                    st.success(f"Payment #{payment_id} logged successfully!")
                    st.session_state.payment_logged = True
                    st.rerun()
    
    with tab2:
        st.subheader("Payment History")
        # Force refresh payments when tab2 is active
        payments = get_payments()
        print(f"Number of payments fetched: {len(payments) if payments else 0}")
        
        if payments:
            # Convert to DataFrame for display
            payment_list = []
            
            for p in payments:
                payment_list.append({
                    "Payment #": p['paymentid'],
                    "Invoice #": p['invoiceid'],
                    "Customer": p['customername'],
                    "Date": p['paymentdate'].split('T')[0] if isinstance(p['paymentdate'], str) else p['paymentdate'].strftime("%Y-%m-%d"),
                    "Method": p['paymentmethod'],
                    "Amount": f"Rs. {float(p['amountpaid']):,.2f}"
                })
            
            print(f"Payment list prepared: {payment_list}")
            df = pd.DataFrame(payment_list)
            st.dataframe(
                df,
                column_config={
                    "Payment #": st.column_config.NumberColumn(format="%d"),
                    "Invoice #": st.column_config.NumberColumn(format="%d"),
                },
                hide_index=True
            )
            
            # Payment details
            if payment_list:
                st.subheader("Payment Details")
                selected_payment_id = st.selectbox(
                    "Select Payment",
                    [p['paymentid'] for p in payments],
                    format_func=lambda x: f"Payment #{x}"
                )
                
                if selected_payment_id:
                    payment = next(p for p in payments if p['paymentid'] == selected_payment_id)
                    
                    st.markdown(f"### Payment #{payment['paymentid']}")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Customer:** {payment['customername']}")
                        st.markdown(f"**Invoice #:** {payment['invoiceid']}")
                        st.markdown(f"**Date:** {payment['paymentdate'].split('T')[0] if isinstance(payment['paymentdate'], str) else payment['paymentdate'].strftime('%Y-%m-%d')}")
                    with col2:
                        st.markdown(f"**Method:** {payment['paymentmethod']}")
                        st.markdown(f"**Amount:** Rs. {float(payment['amountpaid']):,.2f}")
                        st.markdown(f"**Invoice Total:** Rs. {float(payment['grandtotal']):,.2f}")
        else:
            st.info("No payments found")