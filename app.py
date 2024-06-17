import streamlit as st
import pandas as pd
import re
from datetime import datetime

# Function to check email format
def is_valid_email(email):
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None

# Function to check phone number format
def is_valid_phone(phone):
    regex = r'^\+?[0-9]{10,15}$'
    cleaned_phone = re.sub(r'[^0-9]', '', phone.split('x')[0])  # Remove extension if exists
    return re.match(regex, cleaned_phone) is not None

# Function to check card expiry date
def is_valid_expiry(date_str):
    try:
        expiry_date = datetime.strptime(date_str, "%m/%y")
        return expiry_date > datetime.now()
    except ValueError:
        return False

# Function to check account number format
def is_valid_account_number(account_number):
    regex = r'^[A-Z]{2}\d{2}[A-Z0-9]{1,30}$'
    return re.match(regex, account_number) is not None

# Function to check timestamp format
def is_valid_timestamp(timestamp):
    try:
        datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
        return True
    except ValueError:
        return False

# Function to check card number using Luhn algorithm
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

st.title("Adi's Compliance Checker")

uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")
if uploaded_file:
    data = pd.read_excel(uploaded_file)
    compliance_issues = []

    for idx, row in data.iterrows():
        issues = []

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
        if row['Currency'] not in ["USD", "EUR", "GBP"]:  # Simplified currency check
            issues.append(f"Invalid currency code ({row['Currency']})")
        if row['Status'] not in ["Pending", "Completed", "Failed"]:
            issues.append(f"Invalid transaction status ({row['Status']})")
        if not is_valid_timestamp(row['Timestamp']):
            issues.append(f"Invalid timestamp format ({row['Timestamp']})")
        if row['Account Type'] not in ["Savings", "Credit"]:
            issues.append(f"Invalid account type ({row['Account Type']})")
        if row['Transaction Type'] not in ["Debit", "Credit"]:
            issues.append(f"Invalid transaction type ({row['Transaction Type']})")
        if row['Available Balance'] <= 0:
            issues.append(f"Available balance must be positive ({row['Available Balance']})")
        if not re.match(r'^[a-zA-Z\s]+$', row['Customer Name']):
            issues.append(f"Invalid customer name format ({row['Customer Name']})")
        if not is_valid_card_number(row['Card Number']):
            issues.append(f"Invalid card number ({row['Card Number']})")

        if issues:
            compliance_issues.append({
                "Transaction ID": row['Transaction ID'],
                "Issues": "; ".join(issues)
            })

    if compliance_issues:
        st.write("Adi's Compliance Issues Found:")
        st.write(pd.DataFrame(compliance_issues))
    else:
        st.write("No compliance issues found!")
