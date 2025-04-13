# SmartBilling DBMS

A comprehensive Database Management System for billing and invoicing, built with Python Streamlit and Supabase

## Overview

SmartBilling DBMS is a modern web application that helps businesses manage their billing, invoicing, customer relationships, and payment tracking. The system provides a user-friendly interface for handling various aspects of business operations including customer management, invoice generation, payment processing, and reporting.

## Features

- **User Authentication**: Secure login system with role-based access control
- **Customer Management**: Create, view, update, and manage customer information
- **Invoice Generation**: Create and manage invoices with customizable templates
- **Payment Processing**: Track and manage payments with detailed records
- **Reporting**: Generate comprehensive reports and analytics
- **Dashboard**: Interactive dashboard with key business metrics
- **PDF Generation**: Export invoices and reports in PDF format

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: Supabase
- **Key Libraries**:
  - pandas: Data manipulation and analysis
  - plotly: Interactive data visualization
  - fpdf2: PDF generation
  - python-dotenv: Environment variable management
  - supabase: Database operations

## Installation

1. Clone the repository:

```bash
git clone [repository-url]
cd SmartBilling-DBMS
```

2. Create and activate a virtual environment:

```bash
python -m venv smartbilling_env
source smartbilling_env/bin/activate  # On Windows: smartbilling_env\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Create a `.env` file in the root directory
   - Add your Supabase credentials:
     ```
     SUPABASE_URL=your_supabase_url
     SUPABASE_KEY=your_supabase_key
     ```

## Usage

1. Start the application:

```bash
streamlit run app.py
```

2. Open your web browser and navigate to `http://localhost:8501`

3. Log in with your credentials

## Project Structure

- `app.py`: Main application entry point
- `auth.py`: Authentication and user management
- `customers.py`: Customer management functionality
- `invoices.py`: Invoice generation and management
- `payments.py`: Payment processing
- `reports.py`: Reporting and analytics
- `services.py`: Business services management
- `utils.py`: Utility functions and helpers
- `supabase_config.py`: Database configuration
- `dashboard.py`: Dashboard interface
- `login_page.py`: Login interface

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the development team.

Sairaj Bhise{Dev team}- sairajbhise2005@gmail.com

## Acknowledgments

- Documentation- [Amrutheshwari V](https://github.com/Amrutheshwari01)
- Frontend Development- [Lavanya Hs](https://github.com/lavanya-hs15) | [Sampreetha Vishwakarma](https://github.com/Sampreethak)
- Database Design & Implementation - [Sairaj Bhise](https://github.com/SairajBhise2005)
