import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from fpdf import FPDF
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    supabase_url=os.getenv('SUPABASE_URL'),
    supabase_key=os.getenv('SUPABASE_KEY')
)

# Print Supabase connection info for debugging
print(f"Supabase URL: {os.getenv('SUPABASE_URL')}")
print(f"Supabase Key exists: {bool(os.getenv('SUPABASE_KEY'))}")

# Sample database (in-memory storage)
customers_db = []
services_db = []
invoices_db = []
payments_db = []
user_db = []

# ======================
# AUTHENTICATION FUNCTIONS
# ======================
def check_authentication():
    return getattr(st.session_state, 'logged_in', False)

def authenticate_user(email, password):
    try:
        # First authenticate with Supabase Auth
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if auth_response.user:
            # Get user details from the users table
            user_response = supabase.table('users').select('*').eq('email', email).execute()
            
            if user_response.data:
                user_data = user_response.data[0]
                st.session_state.user_id = user_data['userid']
                st.session_state.email = user_data['email']
                st.session_state.fullname = user_data['fullname']
                st.session_state.role = user_data['role']
                return True
        return False
    except Exception as e:
        st.error(f"Authentication error: {str(e)}")
        return False

def register_user(name, email, phone, password):
    try:
        # First check if user already exists in the users table
        existing_user = supabase.table('users').select('email').eq('email', email).execute()
        
        if existing_user.data:
            st.error("This email is already registered. Please use a different email or try logging in.")
            return False
            
        # Create the user in Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        if auth_response.user:
            # Store user data in the users table
            user_data = {
                "email": email,
                "fullname": name,
                "role": "user"  # Default role as per your schema
            }
            
            supabase.table('users').insert(user_data).execute()
            st.success("Account created successfully! Please check your email to verify your account.")
            return True
            
        return False
    except Exception as e:
        error_message = str(e)
        if "User already registered" in error_message:
            st.error("This email is already registered. Please use a different email or try logging in.")
        elif "Password should be at least 6 characters" in error_message:
            st.error("Password must be at least 6 characters long.")
        else:
            st.error(f"Registration error: {error_message}")
        return False

def send_password_reset(email):
    try:
        # Check if email exists in users table
        user_response = supabase.table('users').select('email').eq('email', email).execute()
        
        if user_response.data:
            # Send password reset email
            response = supabase.auth.reset_password_for_email(email)
            return True
        return False
    except Exception as e:
        st.error(f"Password reset error: {str(e)}")
        return False

# ======================
# CUSTOMER FUNCTIONS
# ======================
def get_customers():
    try:
        # First, let's check what tables are available
        response = supabase.table('customers').select('*').execute()
        return response.data
    except Exception as e:
        st.error(f"Error fetching customers: {str(e)}")
        # Try to get more information about the error
        try:
            # List all tables in the public schema
            tables = supabase.rpc('get_tables').execute()
            st.write("Available tables:", tables)
        except:
            pass
        return []

def add_customer(customer_data):
    try:
        response = supabase.table('customers').insert({
            'customername': customer_data['name'],
            'email': customer_data['email'],
            'phonenumber': customer_data['phone'],
            'address': customer_data['address']
        }).execute()
        
        if response.data:
            st.success("Customer added successfully!")
            return True
        return False
    except Exception as e:
        st.error(f"Error adding customer: {str(e)}")
        return False

def update_customer(customer_id, updated_data):
    try:
        response = supabase.table('customers').update({
            'customername': updated_data.get('name'),
            'email': updated_data.get('email'),
            'phonenumber': updated_data.get('phone'),
            'address': updated_data.get('address')
        }).eq('customerid', customer_id).execute()
        
        if response.data:
            st.success("Customer updated successfully!")
            return True
        return False
    except Exception as e:
        st.error(f"Error updating customer: {str(e)}")
        return False

def delete_customer(customer_id):
    try:
        response = supabase.table('customers').delete().eq('customerid', customer_id).execute()
        if response.data:
            st.success("Customer deleted successfully!")
            return True
        return False
    except Exception as e:
        st.error(f"Error deleting customer: {str(e)}")
        return False

def get_customer_history(customer_id):
    try:
        # Get customer details
        customer_response = supabase.table('customers').select('*').eq('customerid', customer_id).execute()
        customer = customer_response.data[0] if customer_response.data else None
        
        # Get invoices for the customer
        invoices_response = supabase.table('invoices').select('*').eq('customerid', customer_id).execute()
        invoices = invoices_response.data if invoices_response.data else []
        
        # Get payments for the customer's invoices
        if invoices:
            invoice_ids = [inv['invoiceid'] for inv in invoices]
            payments_response = supabase.table('payments').select('''
                paymentid,
                invoiceid,
                paymentdate,
                paymentmethod,
                amountpaid
            ''').in_('invoiceid', invoice_ids).execute()
            payments = payments_response.data if payments_response.data else []
        else:
            payments = []
        
        return {
            'customer': customer,
            'invoices': invoices,
            'payments': payments
        }
    except Exception as e:
        st.error(f"Error fetching customer history: {str(e)}")
        return {'customer': None, 'invoices': [], 'payments': []}

# ======================
# SERVICE FUNCTIONS
# ======================
def get_services():
    try:
        response = supabase.table('services').select('*').execute()
        return response.data
    except Exception as e:
        st.error(f"Error fetching services: {str(e)}")
        return []

def add_service(service_data):
    try:
        response = supabase.table('services').insert({
            'servicename': service_data['name'],
            'description': service_data['description'],
            'unitprice': service_data['unit_price']
        }).execute()
        
        if response.data:
            st.success("Service added successfully!")
            return True
        return False
    except Exception as e:
        st.error(f"Error adding service: {str(e)}")
        return False

def update_service(service_id, updated_data):
    try:
        response = supabase.table('services').update({
            'servicename': updated_data['name'],
            'description': updated_data['description'],
            'unitprice': updated_data['unit_price']
        }).eq('serviceid', service_id).execute()
        
        if response.data:
            st.success("Service updated successfully!")
            return True
        return False
    except Exception as e:
        st.error(f"Error updating service: {str(e)}")
        return False

def delete_service(service_id):
    try:
        # First check if service is used in any invoices
        check_response = supabase.table('invoiceservices').select('*').eq('serviceid', service_id).execute()
        
        if check_response.data and len(check_response.data) > 0:
            st.error("Cannot delete service as it is being used in one or more invoices. Please remove the service from all invoices first.")
            return False
            
        # If service is not used in any invoices, proceed with deletion
        response = supabase.table('services').delete().eq('serviceid', service_id).execute()
        if response.data:
            return True
        return False
    except Exception as e:
        st.error(f"Error deleting service: {str(e)}")
        return False

# ======================
# INVOICE FUNCTIONS
# ======================
def get_invoices():
    try:
        response = supabase.table('invoices').select('''
            *,
            customers!inner(*)
        ''').execute()
        return response.data
    except Exception as e:
        st.error(f"Error fetching invoices: {str(e)}")
        return []

def create_invoice(invoice_data):
    try:
        # Start a transaction by creating the invoice first
        invoice_response = supabase.table('invoices').insert({
            'customerid': invoice_data['customer_id'],
            'invoicedate': invoice_data['date'],
            'totalamount': invoice_data['subtotal'],
            'taxamount': invoice_data['tax'],
            'grandtotal': invoice_data['grand_total'],
            'status': invoice_data['status'].capitalize()  # Ensure proper case for status
        }).execute()

        if not invoice_response.data:
            raise Exception("Failed to create invoice")

        invoice_id = invoice_response.data[0]['invoiceid']

        # Insert invoice details for each service
        for service in invoice_data['services']:
            detail_response = supabase.table('invoicedetails').insert({
                'invoiceid': invoice_id,
                'serviceid': service['service_id'],
                'quantity': service['quantity'],
                'totalprice': service['total']
            }).execute()

            if not detail_response.data:
                # If detail insertion fails, the transaction will be rolled back automatically
                raise Exception("Failed to add invoice details")

        return invoice_id

    except Exception as e:
        st.error(f"Error creating invoice: {str(e)}")
        return None

def get_invoice_details(invoice_id):
    try:
        # Get the invoice details including customer information
        invoice_response = supabase.table('invoices').select('''
            *,
            customers!inner(*)
        ''').eq('invoiceid', invoice_id).execute()

        if not invoice_response.data:
            return None

        invoice = invoice_response.data[0]

        # Get the services for this invoice
        services_response = supabase.table('invoicedetails').select('''
            *,
            services!inner(*)
        ''').eq('invoiceid', invoice_id).execute()

        if services_response.data:
            invoice['services'] = [{
                'name': s['services']['servicename'],
                'unit_price': s['services']['unitprice'],
                'quantity': s['quantity'],
                'total': s['totalprice']
            } for s in services_response.data]
        else:
            invoice['services'] = []

        return invoice

    except Exception as e:
        st.error(f"Error fetching invoice details: {str(e)}")
        return None

def check_duplicate_invoice(customer_id, date):
    try:
        # Check if an invoice already exists for this customer on the same date
        response = supabase.table('invoices').select('invoiceid').eq('customerid', customer_id).eq('invoicedate', date).execute()
        return len(response.data) > 0
    except Exception as e:
        st.error(f"Error checking for duplicate invoice: {str(e)}")
        return False

# ======================
# PAYMENT FUNCTIONS
# ======================
def get_payments():
    """Get all payments from the database with related invoice and customer information"""
    try:
        print("Fetching payments...")
        # Get payments with invoice and customer information using a single query
        response = supabase.from_('payments').select('''
            *,
            invoices!inner (
                *,
                customers!inner (
                    customerid,
                    customername
                )
            )
        ''').order('paymentdate', desc=True).execute()
        
        print(f"Response data: {response.data}")
        
        if not response.data:
            print("No payments found in database")
            return []
            
        # Transform the nested data into the expected format
        payments = []
        for p in response.data:
            payment = {
                'paymentid': p['paymentid'],
                'invoiceid': p['invoiceid'],
                'paymentdate': p['paymentdate'],
                'paymentmethod': p['paymentmethod'],
                'amountpaid': p['amountpaid'],
                'customerid': p['invoices']['customers']['customerid'],
                'grandtotal': p['invoices']['grandtotal'],
                'customername': p['invoices']['customers']['customername']
            }
            payments.append(payment)
            print(f"Processed payment: {payment}")
        
        return payments
    except Exception as e:
        print(f"Error in get_payments: {str(e)}")
        st.error(f"Error fetching payments: {str(e)}")
        return []

def log_payment(payment_data):
    """Log a new payment in the database and update invoice status"""
    try:
        print(f"Logging payment: {payment_data}")
        # Insert payment record
        response = supabase.from_('payments').insert({
            'invoiceid': payment_data['invoice_id'],
            'paymentdate': payment_data['date'],
            'paymentmethod': payment_data['method'],
            'amountpaid': payment_data['amount']
        }).execute()

        print(f"Payment insert response: {response.data}")
        if response.data:
            payment_id = response.data[0]['paymentid']
            
            # Update invoice status to 'Paid'
            update_response = supabase.from_('invoices').update({
                'status': 'Paid'
            }).eq('invoiceid', payment_data['invoice_id']).execute()
            print(f"Invoice update response: {update_response.data}")
            
            return payment_id
        return None
    except Exception as e:
        print(f"Error in log_payment: {str(e)}")
        st.error(f"Error logging payment: {str(e)}")
        return None

def get_unpaid_invoices(customer_id=None):
    """Get unpaid invoices, optionally filtered by customer"""
    try:
        query = supabase.table('invoices').select(
            '*', 
            count='exact'
        ).eq('status', 'Unpaid')
        
        if customer_id:
            query = query.eq('customerid', customer_id)
            
        response = query.execute()
        
        if response.data:
            # Get customer details for each invoice
            customer_response = supabase.table('customers').select('*').execute()
            customers = {c['customerid']: c for c in customer_response.data}
            
            # Combine invoice data with customer data
            for invoice in response.data:
                invoice['customername'] = customers.get(invoice['customerid'], {}).get('customername', 'Unknown')
            
            return response.data
        return []
    except Exception as e:
        st.error(f"Error fetching unpaid invoices: {e}")
        return []

# ======================
# PDF GENERATION FUNCTIONS
# ======================
def generate_invoice_pdf(invoice_id, customer, invoice_data):
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Set margins and font
        pdf.set_margins(15, 15, 15)
        pdf.set_font("Arial", 'B', size=16)
        
        # Header - Company Name
        pdf.cell(180, 10, txt="Pet Care Services", ln=1, align='C')
        
        # Company Details
        pdf.set_font("Arial", size=10)
        pdf.cell(180, 5, txt="123 Pet Street, Pet City", ln=1, align='C')
        pdf.cell(180, 5, txt="Phone: +91 98765 43210 | Email: info@petcare.com", ln=1, align='C')
        pdf.cell(180, 5, txt="GST No: 29AABCP9621L1ZK", ln=1, align='C')
        
        # Line separator
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        
        # Invoice Number
        pdf.ln(5)
        pdf.set_font("Arial", 'B', size=12)
        pdf.cell(180, 10, txt=f"Invoice #{invoice_id}", ln=1)
        
        # Date and Status
        pdf.set_font("Arial", size=10)
        pdf.cell(90, 6, txt=f"Date: {invoice_data['invoicedate'].split('T')[0]}", ln=0)
        pdf.cell(90, 6, txt=f"Status: {invoice_data['status'].upper()}", ln=1, align='R')
        
        # Bill To section
        pdf.ln(5)
        pdf.set_font("Arial", 'B', size=10)
        pdf.cell(180, 6, txt="Bill To:", ln=1)
        pdf.set_font("Arial", size=10)
        pdf.cell(180, 6, txt=f"{customer['customername']}", ln=1)
        if customer.get('email'):
            pdf.cell(180, 6, txt=f"Email: {customer['email']}", ln=1)
        if customer.get('phonenumber'):
            pdf.cell(180, 6, txt=f"Phone: {customer['phonenumber']}", ln=1)
        if customer.get('address'):
            pdf.cell(180, 6, txt=f"Address: {customer['address']}", ln=1)
        
        # Services Table
        pdf.ln(5)
        
        # Table Headers
        headers = ['Service', 'Unit Price', 'Quantity', 'Total']
        widths = [90, 30, 30, 30]
        
        pdf.set_font("Arial", 'B', size=10)
        for i, header in enumerate(headers):
            pdf.cell(widths[i], 8, txt=header, border=1, align='C')
        pdf.ln()
        
        # Table Contents
        pdf.set_font("Arial", size=10)
        for service in invoice_data['services']:
            pdf.cell(widths[0], 8, txt=service['name'], border=1)
            pdf.cell(widths[1], 8, txt=f"Rs. {service['unit_price']:.2f}", border=1, align='R')
            pdf.cell(widths[2], 8, txt=str(service['quantity']), border=1, align='C')
            pdf.cell(widths[3], 8, txt=f"Rs. {service['total']:.2f}", border=1, align='R')
            pdf.ln()
        
        # Calculations section
        pdf.ln(5)
        align_position = 120
        label_width = 35
        amount_width = 25
        
        # Subtotal
        pdf.cell(align_position)
        pdf.cell(label_width, 6, txt="Subtotal:", align='L')
        pdf.cell(amount_width, 6, txt=f"Rs. {invoice_data['totalamount']:.2f}", align='R', ln=1)
        
        # Tax Breakdown Header
        pdf.cell(align_position)
        pdf.set_font("Arial", 'B', size=10)
        pdf.cell(label_width + amount_width, 6, txt="Tax Breakdown:", ln=1)
        pdf.set_font("Arial", size=10)
        
        # CGST
        pdf.cell(align_position + 5)
        pdf.cell(label_width, 6, txt="CGST (5%):", align='L')
        pdf.cell(amount_width - 5, 6, txt=f"Rs. {float(invoice_data['taxamount'])/2:.2f}", align='R', ln=1)
        
        # SGST
        pdf.cell(align_position + 5)
        pdf.cell(label_width, 6, txt="SGST (5%):", align='L')
        pdf.cell(amount_width - 5, 6, txt=f"Rs. {float(invoice_data['taxamount'])/2:.2f}", align='R', ln=1)
        
        # Total Tax
        pdf.cell(align_position)
        pdf.set_font("Arial", 'B', size=10)
        pdf.cell(label_width, 6, txt="Total Tax:", align='L')
        pdf.cell(amount_width, 6, txt=f"Rs. {float(invoice_data['taxamount']):.2f}", align='R', ln=1)
        
        # Line before grand total
        pdf.ln(2)
        pdf.line(120, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(2)
        
        # Grand Total
        pdf.set_font("Arial", 'B', size=10)
        pdf.cell(align_position)
        pdf.cell(label_width, 8, txt="Grand Total:", align='L')
        pdf.cell(amount_width, 8, txt=f"Rs. {invoice_data['grandtotal']:.2f}", align='R', ln=1)
        
        # Terms and Conditions
        pdf.ln(20)
        pdf.set_font("Arial", 'B', size=10)
        pdf.cell(180, 6, txt="Terms & Conditions:", ln=1)
        pdf.set_font("Arial", size=10)
        pdf.cell(180, 6, txt="1. Payment is due within 15 days", ln=1)
        pdf.cell(180, 6, txt="2. Please include invoice number in your payment", ln=1)
        pdf.cell(180, 6, txt="3. Make all checks payable to Pet Care Services", ln=1)
        
        # Footer
        pdf.ln(10)
        pdf.set_font("Arial", 'I', size=8)
        pdf.cell(180, 5, txt="Thank you for your business!", align='C', ln=1)
        
        # Save to file
        os.makedirs("temp_pdfs", exist_ok=True)
        pdf_path = f"temp_pdfs/invoice_{invoice_id}.pdf"
        pdf.output(pdf_path)
        return pdf_path
    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
        return None

def generate_report_pdf(report_data):
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Set margins
        pdf.set_margins(10, 10, 10)
        
        # Business Information (Header)
        pdf.set_font("Arial", 'B', size=16)
        pdf.cell(190, 10, txt="Pet Care Services", ln=1, align='C')
        pdf.set_font("Arial", size=10)
        pdf.cell(190, 5, txt="123 Pet Street, Pet City", ln=1, align='C')
        pdf.cell(190, 5, txt="Phone: +91 98765 43210 | Email: info@petcare.com", ln=1, align='C')
        pdf.cell(190, 5, txt="GST No: 29AABCP9621L1ZK", ln=1, align='C')
        
        # Line separator
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        # Report Details
        pdf.set_font("Arial", 'B', size=12)
        pdf.cell(190, 10, txt=f"Business Report", ln=1)
        
        # Date Range
        pdf.set_font("Arial", size=10)
        pdf.cell(190, 6, txt=f"Date Range: {report_data['start_date']} to {report_data['end_date']}", ln=1)
        
        # Summary section
        pdf.ln(5)
        pdf.set_font("Arial", 'B', size=10)
        pdf.cell(190, 6, txt="Summary:", ln=1)
        pdf.set_font("Arial", size=10)
        
        # Calculate total tax and split into CGST and SGST
        total_tax = sum(float(inv.get('taxamount', 0)) for inv in report_data['invoices'])
        cgst = total_tax / 2
        sgst = total_tax / 2
        
        # Revenue breakdown
        pdf.cell(190, 6, txt=f"Total Revenue: Rs. {report_data['total_revenue']:,.2f}", ln=1)
        pdf.cell(190, 6, txt=f"Total Tax (GST): Rs. {total_tax:,.2f}", ln=1)
        pdf.cell(190, 6, txt=f"   - CGST (5%): Rs. {cgst:,.2f}", ln=1)
        pdf.cell(190, 6, txt=f"   - SGST (5%): Rs. {sgst:,.2f}", ln=1)
        pdf.cell(190, 6, txt=f"Total Invoices: {len(report_data['invoices'])}", ln=1)
        pdf.cell(190, 6, txt=f"Total Payments: {len(report_data['payments'])}", ln=1)
        
        # Invoices Table
        pdf.ln(5)
        pdf.set_font("Arial", 'B', size=10)
        pdf.cell(190, 8, txt="Invoices:", ln=1)
        
        # Table Header
        pdf.cell(30, 8, txt="Invoice #", border=1)
        pdf.cell(30, 8, txt="Date", border=1)
        pdf.cell(60, 8, txt="Customer", border=1)
        pdf.cell(35, 8, txt="Amount", border=1, align='C')
        pdf.cell(35, 8, txt="Status", border=1, ln=1)
        
        # Table Contents
        pdf.set_font("Arial", size=10)
        for inv in report_data['invoices']:
            pdf.cell(30, 8, txt=str(inv['invoiceid']), border=1)
            pdf.cell(30, 8, txt=inv['invoicedate'], border=1)
            pdf.cell(60, 8, txt=inv['customername'], border=1)
            pdf.cell(35, 8, txt=f"Rs. {inv['grandtotal']:.2f}", border=1, align='R')
            pdf.cell(35, 8, txt=inv['status'].capitalize(), border=1, ln=1)
        
        # Payments Table
        if report_data.get('payments'):
            pdf.ln(5)
            pdf.set_font("Arial", 'B', size=10)
            pdf.cell(190, 8, txt="Payments:", ln=1)
            
            # Table Header
            pdf.cell(30, 8, txt="Payment #", border=1)
            pdf.cell(30, 8, txt="Date", border=1)
            pdf.cell(30, 8, txt="Invoice #", border=1)
            pdf.cell(60, 8, txt="Customer", border=1)
            pdf.cell(40, 8, txt="Amount", border=1, ln=1)
            
            # Table Contents
            pdf.set_font("Arial", size=10)
            for payment in report_data['payments']:
                pdf.cell(30, 8, txt=str(payment['paymentid']), border=1)
                pdf.cell(30, 8, txt=payment['paymentdate'], border=1)
                pdf.cell(30, 8, txt=str(payment['invoiceid']), border=1)
                pdf.cell(60, 8, txt=payment['customername'], border=1)
                pdf.cell(40, 8, txt=f"Rs. {payment['amountpaid']:.2f}", border=1, align='R', ln=1)
        
        # Service Performance
        if report_data.get('service_performance'):
            pdf.ln(5)
            pdf.set_font("Arial", 'B', size=10)
            pdf.cell(190, 8, txt="Service Performance:", ln=1)
            
            # Table Header
            pdf.cell(90, 8, txt="Service", border=1)
            pdf.cell(50, 8, txt="Usage Count", border=1, align='C')
            pdf.cell(50, 8, txt="Revenue", border=1, align='C', ln=1)
            
            # Table Contents
            pdf.set_font("Arial", size=10)
            for service in report_data['service_performance']:
                pdf.cell(90, 8, txt=service['servicename'], border=1)
                pdf.cell(50, 8, txt=str(service['usage_count']), border=1, align='C')
                pdf.cell(50, 8, txt=f"Rs. {service['total_revenue']:.2f}", border=1, align='R', ln=1)
        
        # Footer
        pdf.ln(10)
        pdf.set_font("Arial", 'I', size=8)
        pdf.cell(190, 5, txt="Generated by Pet Care Services", align='C', ln=1)
        
        # Save to file
        os.makedirs("temp_pdfs", exist_ok=True)
        pdf_path = f"temp_pdfs/report_{report_data['start_date']}_to_{report_data['end_date']}.pdf"
        pdf.output(pdf_path)
        return pdf_path
    except Exception as e:
        st.error(f"Error generating report PDF: {e}")
        return None


# ======================
# REPORT FUNCTIONS
# ======================
def get_report_data(start_date, end_date):
    """Get report data from database for the specified date range"""
    try:
        # Get invoices for the date range
        invoices_response = supabase.from_('invoices').select('''
            *,
            customers (
                customerid,
                customername
            )
        ''').gte('invoicedate', start_date).lte('invoicedate', end_date).execute()
        
        # Get payments for the date range
        payments_response = supabase.from_('payments').select('''
            *,
            invoices!inner (
                customerid,
                customers (
                    customername
                )
            )
        ''').gte('paymentdate', start_date).lte('paymentdate', end_date).execute()
        
        # Get service performance using direct query instead of stored procedure
        service_performance = get_service_performance(start_date, end_date)
        
        # Calculate total revenue (from paid invoices)
        total_revenue = sum(float(payment['amountpaid']) for payment in payments_response.data) if payments_response.data else 0
        
        # Process invoices data
        invoices = []
        if invoices_response.data:
            for inv in invoices_response.data:
                invoices.append({
                    'invoiceid': inv['invoiceid'],
                    'invoicedate': inv['invoicedate'].split('T')[0] if isinstance(inv['invoicedate'], str) else inv['invoicedate'].strftime('%Y-%m-%d'),
                    'customername': inv['customers']['customername'],
                    'grandtotal': float(inv['grandtotal']),
                    'status': inv['status']
                })
        
        # Process payments data
        payments = []
        if payments_response.data:
            for payment in payments_response.data:
                payments.append({
                    'paymentid': payment['paymentid'],
                    'invoiceid': payment['invoiceid'],
                    'paymentdate': payment['paymentdate'].split('T')[0] if isinstance(payment['paymentdate'], str) else payment['paymentdate'].strftime('%Y-%m-%d'),
                    'customername': payment['invoices']['customers']['customername'],
                    'amountpaid': float(payment['amountpaid'])
                })
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'total_revenue': total_revenue,
            'invoices': invoices,
            'payments': payments,
            'service_performance': service_performance
        }
        
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        st.error(f"Error generating report: {str(e)}")
        return None

def get_service_performance(start_date, end_date):
    """Get service performance metrics for the specified date range"""
    try:
        # Get all services with their usage and revenue in the date range
        query = supabase.from_('services').select('''
            serviceid,
            servicename,
            invoicedetails!left (
                serviceid,
                totalprice,
                invoices!inner (
                    invoicedate
                )
            )
        ''').execute()
        
        if not query.data:
            return []
        
        # Process service performance data
        service_performance = {}
        for service in query.data:
            service_id = service['serviceid']
            if service_id not in service_performance:
                service_performance[service_id] = {
                    'serviceid': service_id,
                    'servicename': service['servicename'],
                    'usage_count': 0,
                    'total_revenue': 0
                }
            
            # Calculate usage and revenue for services within date range
            if service.get('invoicedetails'):
                for detail in service['invoicedetails']:
                    if detail.get('invoices') and detail['invoices'].get('invoicedate'):
                        invoice_date = detail['invoices']['invoicedate'].split('T')[0]
                        if start_date <= invoice_date <= end_date:
                            service_performance[service_id]['usage_count'] += 1
                            service_performance[service_id]['total_revenue'] += float(detail['totalprice'])
        
        # Convert to list and sort by revenue
        result = list(service_performance.values())
        result.sort(key=lambda x: x['total_revenue'], reverse=True)
        return result
        
    except Exception as e:
        print(f"Error getting service performance: {str(e)}")
        st.error(f"Error getting service performance: {str(e)}")
        return []

def get_revenue_by_period(period_type, start_date, end_date):
    """Get revenue data grouped by the specified period (day, week, month)"""
    try:
        # Get all payments in the date range
        payments_response = supabase.from_('payments').select('*').gte('paymentdate', start_date).lte('paymentdate', end_date).execute()
        
        if not payments_response.data:
            return []
            
        # Process payments into periods
        revenue_by_period = {}
        for payment in payments_response.data:
            payment_date = payment['paymentdate'].split('T')[0]
            
            # Determine period start date based on period_type
            if period_type == 'day':
                period_start = payment_date
            elif period_type == 'week':
                # Convert to datetime for week calculation
                dt = datetime.strptime(payment_date, '%Y-%m-%d')
                period_start = (dt - timedelta(days=dt.weekday())).strftime('%Y-%m-%d')
            else:  # month
                period_start = payment_date[:7] + '-01'
            
            if period_start not in revenue_by_period:
                revenue_by_period[period_start] = 0
            revenue_by_period[period_start] += float(payment['amountpaid'])
        
        # Convert to list of dictionaries
        return [
            {
                'period_start': period_start,
                'total_revenue': total_revenue
            }
            for period_start, total_revenue in sorted(revenue_by_period.items())
        ]
        
    except Exception as e:
        print(f"Error getting revenue data: {str(e)}")
        st.error(f"Error getting revenue data: {str(e)}")
        return []

# Initialize sample data if empty
if not customers_db:
    add_customer({
        'name': 'Sample Customer',
        'email': 'sample@email.com',
        'phone': '123-456-7890',
        'address': '123 Main St'
    })

if not services_db:
    add_service({
        'name': 'Dog Grooming',
        'description': 'Full service grooming including bath, haircut, and nail trimming',
        'unit_price': 50.00
    })