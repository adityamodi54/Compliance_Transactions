import streamlit as st
import pandas as pd
import re
from datetime import datetime

# Function to check email format using regular expressions
def is_valid_email(email):
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None

# Function to check phone number format
def is_valid_phone(phone):
    regex = r'^\+?[0-9]{10,15}$'
    cleaned_phone = re.sub(r'[^0-9]', '', phone.split('x')[0])
    return re.match(regex, cleaned_phone) is not None

# Function to check if card expiry date is valid and not in the past
def is_valid_expiry(date_str):
    try:
        expiry_date = datetime.strptime(date_str, "%m/%y")
        return expiry_date > datetime.now()
    except ValueError:
        return False

# Function to check if account number follows a valid format
def is_valid_account_number(account_number):
    regex = r'^[A-Z]{2}\d{2}[A-Z0-9]{1,30}$'
    return re.match(regex, account_number) is not None

# Function to check if the timestamp is in a valid ISO 8601 format
def is_valid_timestamp(timestamp):
    try:
        datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
        return True
    except ValueError:
        return False

# Function to check if card number is valid using the Luhn algorithm
def is_valid_card_number(card_number):
    card_number = str(card_number)  # Ensure card_number is a string
    card_number = re.sub(r'[^0-9]', '', card_number)
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(card_number)
    checksum = 0
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum += sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return checksum % 10 == 0

# List of valid account types for validation
valid_account_types = ["Savings", "Credit", "Checking"]

# Streamlit app title
st.title("Adi's Compliance and suspicious transactions Checker")

# File uploader widget to upload an Excel file
uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")
if uploaded_file:
    # Read the uploaded Excel file into a pandas DataFrame
    data = pd.read_excel(uploaded_file)
    
    # Print the column names to verify
    st.write("Column names in the uploaded file:", data.columns)
    
    compliance_issues = []
    suspicious_transactions = []

    # Define the threshold amount for suspicious transactions
    suspicious_amount_threshold = 10000
    # Define high-risk countries for suspicious transactions
    high_risk_countries = ["Country1", "Country2"]

    # Add test transactions for demonstration purposes
    test_transactions = pd.DataFrame([
        {"Transaction ID": "1", "Account Number": "US1234567890", "Customer Email": "test@example.com",
         "Customer Phone": "+1234567890", "Transaction Amount": 15000, "Card Expiry": "12/25",
         "Currency": "USD", "Status": "Completed", "Timestamp": "2023-06-01T12:00:00Z",
         "Account Type": "Savings", "Transaction Type": "Debit", "Available Balance": 5000,
         "Customer Name": "John Doe", "Card Number": "4111111111111111", "Country": "Country1"},
        {"Transaction ID": "2", "Account Number": "US0987654321", "Customer Email": "test2@example.com",
         "Customer Phone": "+10987654321", "Transaction Amount": 500, "Card Expiry": "11/23",
         "Currency": "EUR", "Status": "Pending", "Timestamp": "2023-06-01T13:00:00Z",
         "Account Type": "Checking", "Transaction Type": "Credit", "Available Balance": 1500,
         "Customer Name": "Jane Doe", "Card Number": "4012888888881881", "Country": "Country2"},
        {"Transaction ID": "3", "Account Number": "US1122334455", "Customer Email": "test3@example.com",
         "Customer Phone": "+1122334455", "Transaction Amount": 20000, "Card Expiry": "10/24",
         "Currency": "GBP", "Status": "Failed", "Timestamp": "2023-06-01T14:00:00Z",
         "Account Type": "Credit", "Transaction Type": "Debit", "Available Balance": 1000,
         "Customer Name": "Alice Smith", "Card Number": "5555555555554444", "Country": "Country3"}
    ])
    data = pd.concat([data, test_transactions], ignore_index=True)

    # Ensure all columns have compatible types
    data = data.astype({
        'Transaction ID': 'str',
        'Account Number': 'str',
        'Customer Email': 'str',
        'Customer Phone': 'str',
        'Transaction Amount': 'float',
        'Card Expiry': 'str',
        'Currency': 'str',
        'Status': 'str',
        'Timestamp': 'str',
        'Account Type': 'str',
        'Transaction Type': 'str',
        'Available Balance': 'float',
        'Customer Name': 'str',
        'Card Number': 'str',
        'Country': 'str'
    })

    # Iterate over each row in the DataFrame
    for idx, row in data.iterrows():
        issues = []
        suspicious = False

        # Perform various compliance checks and collect issues
        if not is_valid_account_number(row['Account Number']):
            issues.append("Invalid account number format")
        if not is_valid_email(row['Customer Email']):
            issues.append("Invalid email format")
        if not is_valid_phone(row['Customer Phone']):
            issues.append(f"Invalid phone number format ({row['Customer Phone']})")
        if row['Transaction Amount'] <= 0:
            issues.append(f"Transaction amount must be positive ({row['Transaction Amount']})")
        if not is_valid_expiry(row['Card Expiry']):
            issues.append(f"Card expiry date is invalid or past ({row['Card Expiry']})")
        if row['Currency'] not in ["USD", "EUR", "GBP"]:
            issues.append(f"Invalid currency code ({row['Currency']})")
        if row['Status'] not in ["Pending", "Completed", "Failed"]:
            issues.append(f"Invalid transaction status ({row['Status']})")
        if not is_valid_timestamp(row['Timestamp']):
            issues.append(f"Invalid timestamp format ({row['Timestamp']})")
        if row['Account Type'] not in valid_account_types:
            issues.append(f"Invalid account type ({row['Account Type']})")
        if row['Transaction Type'] not in ["Debit", "Credit"]:
            issues.append(f"Invalid transaction type ({row['Transaction Type']})")
        if row['Available Balance'] <= 0:
            issues.append(f"Available balance must be positive ({row['Available Balance']})")
        if not re.match(r'^[a-zA-Z\s]+$', row['Customer Name']):
            issues.append(f"Invalid customer name format ({row['Customer Name']})")
        if not is_valid_card_number(row['Card Number']):
            issues.append(f"Invalid card number ({row['Card Number']})")

        # Check for suspicious transactions
        if row['Transaction Amount'] > suspicious_amount_threshold:
            suspicious = True
            issues.append(f"Transaction amount exceeds suspicious threshold ({row['Transaction Amount']})")
        if 'Country' in row and row['Country'] in high_risk_countries:
            suspicious = True
            issues.append(f"Transaction involves high-risk country ({row['Country']})")

        if issues:
            compliance_issues.append({
                "Transaction ID": row['Transaction ID'],
                "Issues": "; ".join(issues),
                "Reasons": issues  # Adding the issues as reasons
            })

        # Collect suspicious transactions
        if suspicious:
            suspicious_transactions.append({
                **row.to_dict(),
                "Reasons": [issue for issue in issues if "suspicious" in issue.lower()]
            })

    # Display the compliance issues found, if any
    if compliance_issues:
        st.write("Compliance Issues Found:")
        st.write(pd.DataFrame(compliance_issues))
    else:
        st.write("No compliance issues found!")

    # Display suspicious transactions found, if any
    if suspicious_transactions:
        st.write("Suspicious Transactions Found:")
        st.write(pd.DataFrame(suspicious_transactions))
    else:
        st.write("No suspicious transactions found!")
