import streamlit as st
import pandas as pd
from datetime import datetime
from utils import get_customers, get_services, create_invoice, get_invoices, generate_invoice_pdf, get_invoice_details, check_duplicate_invoice

def show_invoices_page():
    st.title("🐕 Invoice Management")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["Create Invoice", "Invoice List"])
    
    with tab1:
        st.subheader("Create New Invoice")
        
        # Get customers and services
        customers = get_customers()
        services = get_services()
        
        if not customers:
            st.error("No customers available. Please add customers first.")
            return
        if not services:
            st.error("No services available. Please add services first.")
            return
        
        # Store form submission status in session state
        if 'invoice_created' not in st.session_state:
            st.session_state.invoice_created = False
            st.session_state.new_invoice_id = None
            st.session_state.new_invoice_details = None
        
        with st.form("create_invoice_form"):
            # Customer selection
            customer_id = st.selectbox(
                "Select Customer",
                [c['customerid'] for c in customers],
                format_func=lambda x: f"{next(c['customername'] for c in customers if c['customerid'] == x)}"
            )
            
            # Date selection
            invoice_date = st.date_input("Invoice Date", datetime.now())
            
            # Service selection
            st.subheader("Add Services")
            
            # Initialize service count in session state
            if 'service_count' not in st.session_state:
                st.session_state.service_count = 1
            
            selected_services = []
            service_ids_selected = set()  # Track selected service IDs
            
            for i in range(st.session_state.service_count):
                col1, col2 = st.columns([3, 1])
                with col1:
                    service_id = st.selectbox(
                        f"Service {i+1}",
                        [s['serviceid'] for s in services],
                        format_func=lambda x: f"{next(s['servicename'] for s in services if s['serviceid'] == x)} (Rs. {next(s['unitprice'] for s in services if s['serviceid'] == x):.2f})",
                        key=f"service_{i}"
                    )
                with col2:
                    quantity = st.number_input(
                        "Quantity",
                        min_value=1,
                        value=1,
                        key=f"quantity_{i}"
                    )
                
                if service_id:
                    if service_id in service_ids_selected:
                        st.error(f"Service {next(s['servicename'] for s in services if s['serviceid'] == service_id)} is selected multiple times. Please select each service only once.")
                    else:
                        service_ids_selected.add(service_id)
                        service = next(s for s in services if s['serviceid'] == service_id)
                        selected_services.append({
                            "service_id": service_id,
                            "name": service['servicename'],
                            "unit_price": service['unitprice'],
                            "quantity": quantity,
                            "total": service['unitprice'] * quantity
                        })
            
            # Add/Remove service buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("➕ Add Service"):
                    st.session_state.service_count += 1
                    st.rerun()
            with col2:
                if st.session_state.service_count > 1:
                    if st.form_submit_button("➖ Remove Service"):
                        st.session_state.service_count -= 1
                        st.rerun()
            
            # Status selection
            status = st.radio("Invoice Status", ["Unpaid", "Paid"])
            
            # Calculate totals if services are selected
            if selected_services:
                subtotal = sum(s['total'] for s in selected_services)
                tax_rate = 0.10  # 10% tax
                tax_amount = subtotal * tax_rate
                cgst = tax_amount / 2
                sgst = tax_amount / 2
                grand_total = subtotal + tax_amount
                
                # Preview section inside form
                st.markdown("### Invoice Preview")
                st.markdown("#### Services")
                preview_df = pd.DataFrame([{
                    'Service': s['name'],
                    'Unit Price': f"Rs. {s['unit_price']:,.2f}",
                    'Quantity': s['quantity'],
                    'Total': f"Rs. {s['total']:,.2f}"
                } for s in selected_services])
                st.table(preview_df)
                
                # Show totals
                st.markdown("#### Amount Details")
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.markdown("**Subtotal:**")
                    st.markdown("**CGST (5%):**")
                    st.markdown("**SGST (5%):**")
                    st.markdown("**Grand Total:**")
                with col2:
                    st.markdown(f"**Rs. {subtotal:,.2f}**")
                    st.markdown(f"**Rs. {cgst:,.2f}**")
                    st.markdown(f"**Rs. {sgst:,.2f}**")
                    st.markdown(f"**Rs. {grand_total:,.2f}**")
            
            # Submit button
            submit_button = st.form_submit_button("Create Invoice")
            
            if submit_button:
                if not selected_services:
                    st.error("Please add at least one service")
                elif check_duplicate_invoice(customer_id, invoice_date.strftime("%Y-%m-%d")):
                    st.error("An invoice already exists for this customer on the selected date")
                else:
                    invoice_data = {
                        "customer_id": customer_id,
                        "date": invoice_date.strftime("%Y-%m-%d"),
                        "services": selected_services,
                        "subtotal": subtotal,
                        "tax": tax_amount,
                        "cgst": cgst,
                        "sgst": sgst,
                        "grand_total": grand_total,
                        "status": status
                    }
                    
                    invoice_id = create_invoice(invoice_data)
                    if invoice_id:
                        st.session_state.invoice_created = True
                        st.session_state.new_invoice_id = invoice_id
                        st.session_state.new_invoice_details = get_invoice_details(invoice_id)
                        st.success(f"Invoice #{invoice_id} created successfully!")
        
        # PDF Generation and Download - Outside the form
        if st.session_state.invoice_created and st.session_state.new_invoice_id and st.session_state.new_invoice_details:
            invoice_details = st.session_state.new_invoice_details
            customer = next(c for c in customers if c['customerid'] == invoice_details['customerid'])
            
            # Show final preview before download
            st.markdown("### Final Invoice Preview")
            
            # Customer and Invoice Info
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Invoice #:** {st.session_state.new_invoice_id}")
                st.markdown(f"**Date:** {invoice_details['invoicedate'].split('T')[0]}")
                st.markdown(f"**Status:** {invoice_details['status']}")
            with col2:
                st.markdown(f"**Customer:** {customer['customername']}")
                if customer.get('email'):
                    st.markdown(f"**Email:** {customer['email']}")
                if customer.get('phonenumber'):
                    st.markdown(f"**Phone:** {customer['phonenumber']}")
            
            # Services
            st.markdown("#### Services")
            services_df = pd.DataFrame([{
                'Service': s['name'],
                'Unit Price': f"Rs. {s['unit_price']:,.2f}",
                'Quantity': s['quantity'],
                'Total': f"Rs. {s['total']:,.2f}"
            } for s in invoice_details['services']])
            st.table(services_df)
            
            # Amount Details
            st.markdown("#### Amount Details")
            amount_col1, amount_col2 = st.columns([1, 1])
            with amount_col1:
                st.markdown("**Subtotal:**")
                st.markdown("**CGST (5%):**")
                st.markdown("**SGST (5%):**")
                st.markdown("**Grand Total:**")
            with amount_col2:
                st.markdown(f"**Rs. {invoice_details['totalamount']:,.2f}**")
                st.markdown(f"**Rs. {invoice_details['taxamount']/2:,.2f}**")
                st.markdown(f"**Rs. {invoice_details['taxamount']/2:,.2f}**")
                st.markdown(f"**Rs. {invoice_details['grandtotal']:,.2f}**")
            
            # Generate PDF path but don't show download button yet
            pdf_path = generate_invoice_pdf(st.session_state.new_invoice_id, customer, invoice_details)
            if pdf_path:
                st.session_state.current_pdf_path = pdf_path
                st.session_state.current_invoice_id = st.session_state.new_invoice_id

    with tab2:
        st.subheader("Invoice List")
        invoices = get_invoices()
        
        if invoices:
            # Convert to DataFrame for display
            invoice_list = []
            for inv in invoices:
                invoice_list.append({
                    "Invoice #": inv['invoiceid'],
                    "Customer": inv['customers']['customername'],
                    "Date": inv['invoicedate'].split('T')[0],
                    "Amount": f"Rs. {inv['grandtotal']:,.2f}",
                    "Status": inv['status']
                })
            
            df = pd.DataFrame(invoice_list)
            st.dataframe(df)
            
            # Invoice details section
            st.subheader("Invoice Details")
            
            # Create two columns for the layout
            col1, col2 = st.columns([2, 1])
            
            with col1:
                selected_invoice_id = st.selectbox(
                    "Select Invoice",
                    [inv['invoiceid'] for inv in invoices],
                    format_func=lambda x: f"Invoice #{x} - {next(inv['customers']['customername'] for inv in invoices if inv['invoiceid'] == x)}"
                )
            
            if selected_invoice_id:
                invoice_details = get_invoice_details(selected_invoice_id)
                if invoice_details:
                    # Display invoice details
                    st.markdown(f"### Invoice #{invoice_details['invoiceid']}")
                    detail_col1, detail_col2 = st.columns(2)
                    with detail_col1:
                        st.markdown(f"**Customer:** {invoice_details['customers']['customername']}")
                        st.markdown(f"**Date:** {invoice_details['invoicedate'].split('T')[0]}")
                        st.markdown(f"**Status:** {invoice_details['status']}")
                    with detail_col2:
                        st.markdown(f"**Subtotal:** Rs. {invoice_details['totalamount']:,.2f}")
                        st.markdown(f"**Tax:** Rs. {invoice_details['taxamount']:,.2f}")
                        st.markdown(f"**Grand Total:** Rs. {invoice_details['grandtotal']:,.2f}")
                    
                    # Display services
                    st.markdown("#### Services")
                    if invoice_details['services']:
                        services_df = pd.DataFrame([{
                            'Service': s['name'],
                            'Unit Price': f"Rs. {s['unit_price']:,.2f}",
                            'Quantity': s['quantity'],
                            'Total': f"Rs. {s['total']:,.2f}"
                        } for s in invoice_details['services']])
                        st.table(services_df)
                    
                    # Generate PDF but don't show download button yet
                    customer = invoice_details['customers']
                    pdf_path = generate_invoice_pdf(selected_invoice_id, customer, invoice_details)
                    if pdf_path:
                        st.session_state.current_pdf_path = pdf_path
                        st.session_state.current_invoice_id = selected_invoice_id
        else:
            st.info("No invoices found")

    # Add spacing before the download section
    st.markdown("---")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Move PDF download section to the very bottom of the page
    if hasattr(st.session_state, 'current_pdf_path') and st.session_state.current_pdf_path:
        col1, col2 = st.columns([1, 1])
        with col1:
            with open(st.session_state.current_pdf_path, "rb") as f:
                st.download_button(
                    "📥 Download Invoice as PDF",
                    f,
                    file_name=f"invoice_{st.session_state.current_invoice_id}.pdf",
                    mime="application/pdf",
                    key=f"download_invoice_{st.session_state.current_invoice_id}"
                )
        with col2:
            if st.button("Create Another Invoice"):
                st.session_state.invoice_created = False
                st.session_state.new_invoice_id = None
                st.session_state.new_invoice_details = None
                st.session_state.current_pdf_path = None
                st.session_state.current_invoice_id = None
                st.rerun()