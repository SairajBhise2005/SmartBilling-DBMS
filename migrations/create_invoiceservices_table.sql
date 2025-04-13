-- Create the invoiceservices table
CREATE TABLE IF NOT EXISTS public.users (
    userid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR NOT NULL,
    fullname VARCHAR,
    role VARCHAR,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS public.services (
    serviceid SERIAL PRIMARY KEY,
    servicename VARCHAR NOT NULL,
    description TEXT,
    unitprice NUMERIC NOT NULL
);

CREATE TABLE IF NOT EXISTS public.customers (
    customerid SERIAL PRIMARY KEY,
    customername VARCHAR NOT NULL,
    email VARCHAR,
    phonenumber VARCHAR,
    addr TEXT,
    createddate TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS public.invoices (
    invoiceid SERIAL PRIMARY KEY,
    customerid INTEGER NOT NULL REFERENCES public.customers(customerid),
    invoicedate TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    totalamount NUMERIC NOT NULL DEFAULT 0,
    taxamount NUMERIC NOT NULL DEFAULT 0,
    grandtotal NUMERIC NOT NULL DEFAULT 0,
    status TEXT DEFAULT 'pending',
    CONSTRAINT fk_customer FOREIGN KEY (customerid) REFERENCES public.customers(customerid)
);

CREATE TABLE IF NOT EXISTS public.invoiceservices (
    invoiceid INTEGER NOT NULL,
    serviceid INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    totalprice NUMERIC NOT NULL,
    CONSTRAINT pk_invoiceservices PRIMARY KEY (invoiceid, serviceid),
    CONSTRAINT fk_invoice FOREIGN KEY (invoiceid) REFERENCES public.invoices(invoiceid),
    CONSTRAINT fk_service FOREIGN KEY (serviceid) REFERENCES public.services(serviceid)
);

CREATE TABLE IF NOT EXISTS public.payments (
    paymentid SERIAL PRIMARY KEY,
    invoiceid INTEGER NOT NULL,
    paymentdate TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    paymentmethod TEXT NOT NULL,
    amountpaid NUMERIC NOT NULL,
    CONSTRAINT fk_invoice FOREIGN KEY (invoiceid) REFERENCES public.invoices(invoiceid)
);

CREATE TABLE IF NOT EXISTS public.taxes (
    taxid SERIAL PRIMARY KEY,
    taxname VARCHAR NOT NULL,
    taxrate NUMERIC NOT NULL
); 