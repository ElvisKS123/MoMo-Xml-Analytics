#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generate sample SMS data for MoMo Data Analysis
"""

import os
import sys
import random
import datetime
import xml.dom.minidom as md
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

# Constants
OUTPUT_FILE = project_root / "data" / "raw" / "generated_sms_data.xml"
NUM_MESSAGES = 100
START_DATE = datetime.datetime(2023, 1, 1)
END_DATE = datetime.datetime(2023, 5, 31)

# Transaction types and their templates
TRANSACTION_TEMPLATES = {
    "CASH_IN": [
        "You have received RWF {amount:.0f} from {name} ({phone}) on {date} at {time}. Reference: {reference}. Fee charged: RWF {fee:.0f}. Available Balance: RWF {balance:,.0f}",
        "MoMo deposit received. RWF {amount:.0f} from {name} ({phone}). Date: {date} {time}. Ref: {reference}. Fee: RWF {fee:.0f}. New balance: RWF {balance:,.0f}"
    ],
    "CASH_OUT": [
        "You have withdrawn RWF {amount:.0f} from {name} ({phone}) on {date} at {time}. Reference: {reference}. Fee charged: RWF {fee:.0f}. Available Balance: RWF {balance:,.0f}",
        "MoMo withdrawal completed. RWF {amount:.0f} to {name} ({phone}). Date: {date} {time}. Ref: {reference}. Fee: RWF {fee:.0f}. New balance: RWF {balance:,.0f}"
    ],
    "PAYMENT": [
        "You have paid RWF {amount:.0f} to {name} ({phone}) on {date} at {time}. Reference: {reference}. Fee charged: RWF {fee:.0f}. Available Balance: RWF {balance:,.0f}",
        "Payment of RWF {amount:.0f} to {name} ({phone}) successful. Date: {date} {time}. Ref: {reference}. Fee: RWF {fee:.0f}. New balance: RWF {balance:,.0f}"
    ],
    "TRANSFER": [
        "You have sent RWF {amount:.0f} to {name} ({phone}) on {date} at {time}. Reference: {reference}. Fee charged: RWF {fee:.0f}. Available Balance: RWF {balance:,.0f}",
        "Transfer of RWF {amount:.0f} to {name} ({phone}) completed. Date: {date} {time}. Ref: {reference}. Fee: RWF {fee:.0f}. New balance: RWF {balance:,.0f}"
    ]
}

# Names and descriptions for transactions
NAMES = {
    "CASH_IN": [
        "JOHN DOE", "MARY SMITH", "SALARY PAYMENT", "BUSINESS INCOME", 
        "GIFT PAYMENT", "LOAN DISBURSEMENT", "REFUND", "INVESTMENT RETURN"
    ],
    "CASH_OUT": [
        "AGENT KOFI", "AGENT SARAH", "AGENT PETER", "ATM WITHDRAWAL", 
        "BANK TRANSFER", "CASH POINT", "AGENT EXPRESS", "QUICK CASH"
    ],
    "PAYMENT": [
        "ECG PREPAID", "WATER BILL", "DSTV SUBSCRIPTION", "SCHOOL FEES", 
        "INTERNET BUNDLE", "ELECTRICITY BILL", "INSURANCE PREMIUM", "TAX PAYMENT",
        "HOSPITAL BILL", "RENT PAYMENT"
    ],
    "TRANSFER": [
        "JANE SMITH", "MARY JOHNSON", "CHARITY DONATION", "FAMILY SUPPORT", 
        "BUSINESS PARTNER", "SAVINGS ACCOUNT", "INVESTMENT FUND", "AIRTIME PURCHASE"
    ]
}

def random_date(start, end):
    """Generate a random date between start and end"""
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + datetime.timedelta(seconds=random_second)

def random_phone():
    """Generate a random Ghana phone number"""
    prefixes = ["024", "054", "055", "027", "057", "026", "056", "030"]
    prefix = random.choice(prefixes)
    suffix = ''.join(random.choices('0123456789', k=7))
    return f"{prefix}{suffix}"

def random_reference():
    """Generate a random transaction reference"""
    return f"TX{''.join(random.choices('0123456789', k=9))}"

def generate_transaction(msg_id, date):
    """Generate a random transaction"""
    # Select transaction type
    tx_type = random.choice(list(TRANSACTION_TEMPLATES.keys()))
    
    # Format date and time
    date_str = date.strftime("%d/%m/%y")
    time_str = date.strftime("%I:%M %p")
    
    # Generate random values
    amount = round(random.uniform(10, 2000), 2)
    name = random.choice(NAMES[tx_type])
    phone = random_phone()
    reference = random_reference()
    
    # Calculate fee based on amount and type
    if tx_type == "CASH_IN":
        fee = 0.0
    else:
        fee = round(amount * 0.01, 2)  # 1% fee
    
    # Maintain a running balance
    if msg_id == 1:
        balance = 1000.0  # Starting balance
    else:
        # This is simplified - in reality would need to track previous balance
        balance = round(random.uniform(500, 5000), 2)
    
    # Adjust balance based on transaction
    if tx_type == "CASH_IN":
        balance += amount
    else:
        balance -= (amount + fee)
    
    # Select a template and format the message
    template = random.choice(TRANSACTION_TEMPLATES[tx_type])
    content = template.format(
        amount=amount,
        name=name,
        phone=phone,
        date=date_str,
        time=time_str,
        reference=reference,
        fee=fee,
        balance=balance
    )
    
    return {
        "id": msg_id,
        "date": date.strftime("%Y-%m-%d %H:%M:%S"),
        "sender": "MTN MOMO",
        "content": content
    }

def create_xml_document(messages):
    """Create an XML document from messages"""
    doc = md.getDOMImplementation().createDocument(None, "messages", None)
    root = doc.documentElement
    
    for msg in messages:
        message_elem = doc.createElement("message")
        
        # Add message elements
        for key, value in msg.items():
            elem = doc.createElement(key)
            text = doc.createTextNode(str(value))
            elem.appendChild(text)
            message_elem.appendChild(elem)
        
        root.appendChild(message_elem)
    
    return doc

def generate_sample_data(num_messages=NUM_MESSAGES):
    """Generate sample SMS data"""
    messages = []
    
    # Generate random messages
    for i in range(1, num_messages + 1):
        date = random_date(START_DATE, END_DATE)
        message = generate_transaction(i, date)
        messages.append(message)
    
    # Sort messages by date
    messages.sort(key=lambda x: x["date"])
    
    # Update IDs after sorting
    for i, msg in enumerate(messages, 1):
        msg["id"] = i
    
    return messages

def save_to_xml(messages, output_file):
    """Save messages to XML file"""
    # Create XML document
    doc = create_xml_document(messages)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Write to file with pretty formatting
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(doc.toprettyxml(indent="    "))
    
    print(f"Generated {len(messages)} sample messages and saved to {output_file}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate sample SMS data for MoMo Data Analysis")
    parser.add_argument(
        "-n", "--num-messages", 
        type=int, 
        default=NUM_MESSAGES,
        help=f"Number of messages to generate (default: {NUM_MESSAGES})"
    )
    parser.add_argument(
        "-o", "--output", 
        type=str, 
        default=str(OUTPUT_FILE),
        help=f"Output file path (default: {OUTPUT_FILE})"
    )
    
    args = parser.parse_args()
    
    # Generate and save sample data
    messages = generate_sample_data(args.num_messages)
    save_to_xml(messages, args.output)

if __name__ == "__main__":
    main()