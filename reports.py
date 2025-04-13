import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from utils import get_report_data, get_service_performance, get_revenue_by_period, generate_report_pdf
import os

def show_reports_page():
    st.title("🐕 Business Reports")
    st.markdown("---")
    
    # Date range selection
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=None)
    with col2:
        end_date = st.date_input("End Date", value=None)
    
    # Validate date selection
    if not start_date or not end_date:
        st.info("Please select both start and end dates to generate the report")
        return
        
    if start_date > end_date:
        st.error("Start date must be before end date")
        return
    
    # Get report data
    report_data = get_report_data(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    
    if not report_data:
        st.warning("No data available for the selected date range")
        return
    
    # Summary metrics
    st.subheader("Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Revenue", f"Rs. {report_data['total_revenue']:,.2f}")
    with col2:
        total_invoices = len(report_data['invoices'])
        st.metric("Total Invoices", total_invoices)
    with col3:
        total_payments = len(report_data['payments'])
        st.metric("Total Payments", total_payments)
    
    # Revenue trend
    st.subheader("Revenue Trend")
    period = st.selectbox("Group by", ["day", "week", "month"])
    revenue_data = get_revenue_by_period(period, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    
    if revenue_data:
        df_revenue = pd.DataFrame(revenue_data)
        fig = px.line(df_revenue, x='period_start', y='total_revenue',
                     title=f"Revenue Trend by {period.capitalize()}",
                     labels={'period_start': 'Date', 'total_revenue': 'Revenue (Rs.)'})
        st.plotly_chart(fig)
    
    # Service Performance
    st.subheader("Service Performance")
    if report_data['service_performance']:
        df_services = pd.DataFrame(report_data['service_performance'])
        
        # Bar chart for service usage
        fig_usage = px.bar(df_services, x='servicename', y='usage_count',
                          title="Service Usage Count",
                          labels={'servicename': 'Service', 'usage_count': 'Number of Times Used'})
        st.plotly_chart(fig_usage)
        
        # Bar chart for service revenue
        fig_revenue = px.bar(df_services, x='servicename', y='total_revenue',
                           title="Service Revenue",
                           labels={'servicename': 'Service', 'total_revenue': 'Revenue (Rs.)'})
        st.plotly_chart(fig_revenue)
    
    # Invoices and Payments Tables
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Recent Invoices")
        if report_data['invoices']:
            df_invoices = pd.DataFrame(report_data['invoices'])
            st.dataframe(
                df_invoices,
                column_config={
                    "invoiceid": "Invoice #",
                    "invoicedate": "Date",
                    "customername": "Customer",
                    "grandtotal": st.column_config.NumberColumn(
                        "Amount",
                        format="Rs. %.2f"
                    ),
                    "status": "Status"
                },
                hide_index=True
            )
    
    with col2:
        st.subheader("Recent Payments")
        if report_data['payments']:
            df_payments = pd.DataFrame(report_data['payments'])
            st.dataframe(
                df_payments,
                column_config={
                    "paymentid": "Payment #",
                    "invoiceid": "Invoice #",
                    "paymentdate": "Date",
                    "customername": "Customer",
                    "amountpaid": st.column_config.NumberColumn(
                        "Amount",
                        format="Rs. %.2f"
                    )
                },
                hide_index=True
            )
    
    # Generate and Download Report
    st.markdown("---")
    
    # Prepare report data and PDF if we have data
    if report_data:
        pdf_path = generate_report_pdf(report_data)
        if pdf_path:
            with open(pdf_path, 'rb') as pdf_file:
                pdf_data = pdf_file.read()
            # Clean up the temporary file
            try:
                os.remove(pdf_path)
            except:
                pass
            # Show single button for generation and download
            st.download_button(
                label="📊 Generate & Download Report",
                data=pdf_data,
                file_name=f"business_report_{start_date}_to_{end_date}.pdf",
                mime="application/pdf"
            )
    else:
        # Disabled button if no data
        st.button("📊 Generate & Download Report", disabled=True, help="No data available for the selected date range")