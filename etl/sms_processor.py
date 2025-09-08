#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MoMo SMS Data Processor

This script processes MoMo SMS data from XML format, categorizes transactions,
and loads the processed data into a SQLite database.
"""

import os
import sys
import logging
import json
import sqlite3
import xmltodict
import pandas as pd
from datetime import datetime
from dateutil import parser
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('data', 'logs', 'etl.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('momo_etl')

# Configure dead letter queue
dead_letter_path = os.path.join('data', 'logs', 'dead_letter')
os.makedirs(dead_letter_path, exist_ok=True)


class MomoSmsProcessor:
    """Process MoMo SMS data from XML to structured format and load into database."""
    
    # Transaction type keywords
    CASH_IN_KEYWORDS = ['received', 'cash in', 'payment received', 'paid']
    CASH_OUT_KEYWORDS = ['withdrew', 'cash out', 'paid', 'payment']
    
    # Transaction categories
    CATEGORIES = {
        'bills': ['bill', 'dstv', 'electricity', 'water', 'utility'],
        'shopping': ['shop', 'store', 'market', 'mall', 'purchase'],
        'food': ['food', 'restaurant', 'cafe', 'meal', 'grocery'],
        'transport': ['transport', 'uber', 'taxi', 'fare', 'ride'],
        'entertainment': ['entertainment', 'movie', 'cinema', 'game', 'ticket'],
        'education': ['school', 'tuition', 'fee', 'education', 'college'],
        'health': ['health', 'hospital', 'medical', 'pharmacy', 'doctor'],
        'transfer': ['transfer', 'sent to', 'received from'],
        'airtime': ['airtime', 'data', 'bundle', 'credit', 'recharge'],
        'withdrawal': ['withdraw', 'atm', 'agent', 'cash out'],
        'deposit': ['deposit', 'cash in', 'load'],
        'salary': ['salary', 'payroll', 'wage', 'income'],
        'savings': ['save', 'savings', 'investment'],
        'loan': ['loan', 'borrow', 'credit', 'debt'],
        'other': []
    }
    
    def __init__(self, xml_path: str, db_path: str):
        """Initialize the processor with file paths.
        
        Args:
            xml_path: Path to the XML file containing SMS data
            db_path: Path to the SQLite database
        """
        self.xml_path = xml_path
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.transactions = []
        
    def connect_db(self) -> None:
        """Connect to SQLite database and create tables if they don't exist."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            
            # Create transactions table if it doesn't exist
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    description TEXT NOT NULL,
                    amount REAL NOT NULL,
                    type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    phone TEXT,
                    reference TEXT,
                    processed_date TEXT NOT NULL
                )
            ''')
            
            # Check if date column exists and add it if it doesn't
            try:
                self.cursor.execute("SELECT date FROM transactions LIMIT 1")
            except sqlite3.OperationalError:
                # Column doesn't exist, add it
                self.cursor.execute("ALTER TABLE transactions ADD COLUMN date TEXT")
            
            # Create stats table if it doesn't exist
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stat_name TEXT NOT NULL,
                    stat_value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            self.conn.commit()
            logger.info("Database connection established and tables created if needed")
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            raise
    
    def read_xml(self) -> List[Dict[str, Any]]:
        """Read SMS data from XML file.
        
        Returns:
            List of SMS message dictionaries
        """
        try:
            with open(self.xml_path, 'r', encoding='utf-8') as file:
                xml_content = file.read()
            
            # Parse XML to dict
            data_dict = xmltodict.parse(xml_content)
            
            # Extract SMS messages
            if 'smses' in data_dict and 'sms' in data_dict['smses']:
                messages = data_dict['smses']['sms']
                if isinstance(messages, dict):  # Single message
                    messages = [messages]
                logger.info(f"Successfully read {len(messages)} SMS messages from XML")
                return messages
            else:
                logger.error("XML structure not as expected")
                return []
        except Exception as e:
            logger.error(f"Error reading XML file: {e}")
            return []
    
    def is_momo_sms(self, message: Dict[str, Any]) -> bool:
        """Check if an SMS is a MoMo transaction.
        
        Args:
            message: SMS message dictionary
            
        Returns:
            True if the message is a MoMo transaction, False otherwise
        """
        if '@body' not in message:
            return False
            
        body = message['@body'].lower()
        
        # Check if it's from MoMo (usually contains these keywords)
        momo_indicators = ['momo', 'mobile money', 'transaction', 'received', 
                          'sent', 'cash in', 'cash out', 'withdraw', 'deposit']
        
        return any(indicator in body for indicator in momo_indicators)
    
    def extract_transaction_details(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract transaction details from a MoMo SMS.
        
        Args:
            message: SMS message dictionary
            
        Returns:
            Dictionary with transaction details or None if extraction fails
        """
        try:
            body = message['@body']
            date_str = message.get('@date', '')
            
            # Convert timestamp to datetime
            if date_str:
                try:
                    # Convert milliseconds since epoch to datetime
                    date = datetime.fromtimestamp(int(date_str) / 1000)
                except (ValueError, TypeError):
                    date = datetime.now()
            else:
                date = datetime.now()
            
            # Extract amount using common patterns
            amount = 0.0
            amount_patterns = [
                r'RWF\s*([\d,.]+)',  # RWF 100.00
                r'([\d,.]+)\s*RWF',  # 100.00 RWF
                r'amount[:\s]*RWF\s*([\d,.]+)',  # amount: RWF 100.00
                r'amount[:\s]*([\d,.]+)',  # amount: 100.00
                r'([\d,.]+)\s*francs'  # 100.00 francs
            ]
            
            for pattern in amount_patterns:
                import re
                match = re.search(pattern, body, re.IGNORECASE)
                if match:
                    amount_str = match.group(1).replace(',', '')
                    try:
                        amount = float(amount_str)
                        break
                    except ValueError:
                        continue
            
            # Determine transaction type
            body_lower = body.lower()
            if any(keyword in body_lower for keyword in self.CASH_IN_KEYWORDS):
                transaction_type = 'CASH_IN'
            elif any(keyword in body_lower for keyword in self.CASH_OUT_KEYWORDS):
                transaction_type = 'CASH_OUT'
            else:
                transaction_type = 'OTHER'
            
            # Extract phone number if present
            phone_match = re.search(r'(?:\+|0)[\d\s]{9,}', body)
            phone = phone_match.group().strip() if phone_match else None
            
            # Extract reference if present
            ref_patterns = [
                r'ref[:\s]*(\w+)',  # ref: ABC123
                r'reference[:\s]*(\w+)',  # reference: ABC123
                r'id[:\s]*(\w+)'  # id: ABC123
            ]
            
            reference = None
            for pattern in ref_patterns:
                match = re.search(pattern, body, re.IGNORECASE)
                if match:
                    reference = match.group(1)
                    break
            
            # Categorize transaction
            category = self.categorize_transaction(body_lower)
            
            return {
                'date': date.strftime('%Y-%m-%d %H:%M:%S'),
                'description': body,
                'amount': amount,
                'type': transaction_type,
                'category': category,
                'phone': phone,
                'reference': reference,
                'processed_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            logger.error(f"Error extracting transaction details: {e}")
            # Save to dead letter queue
            self.save_to_dead_letter(message, str(e))
            return None
    
    def categorize_transaction(self, description: str) -> str:
        """Categorize a transaction based on its description.
        
        Args:
            description: Transaction description text
            
        Returns:
            Category name
        """
        for category, keywords in self.CATEGORIES.items():
            if any(keyword in description for keyword in keywords):
                return category
        return 'other'
    
    def save_to_dead_letter(self, message: Dict[str, Any], error: str) -> None:
        """Save problematic messages to dead letter queue.
        
        Args:
            message: The message that couldn't be processed
            error: Error description
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"dead_letter_{timestamp}.json"
            filepath = os.path.join(dead_letter_path, filename)
            
            with open(filepath, 'w') as file:
                json.dump({
                    'message': message,
                    'error': error,
                    'timestamp': timestamp
                }, file, indent=2)
                
            logger.info(f"Message saved to dead letter queue: {filepath}")
        except Exception as e:
            logger.error(f"Error saving to dead letter queue: {e}")
    
    def save_to_db(self) -> None:
        """Save processed transactions to database."""
        if not self.transactions:
            logger.warning("No transactions to save")
            return
            
        try:
            # Insert transactions
            for transaction in self.transactions:
                self.cursor.execute('''
                    INSERT INTO transactions 
                    (date, description, amount, type, category, phone, reference, processed_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    transaction['date'],
                    transaction['description'],
                    transaction['amount'],
                    transaction['type'],
                    transaction['category'],
                    transaction['phone'],
                    transaction['reference'],
                    transaction['processed_date']
                ))
            
            # Update stats
            stats = self.calculate_stats()
            for stat_name, stat_value in stats.items():
                # Check if stat exists
                self.cursor.execute('''
                    SELECT id FROM stats WHERE stat_name = ?
                ''', (stat_name,))
                
                result = self.cursor.fetchone()
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                if result:
                    # Update existing stat
                    self.cursor.execute('''
                        UPDATE stats SET stat_value = ?, updated_at = ? WHERE stat_name = ?
                    ''', (str(stat_value), timestamp, stat_name))
                else:
                    # Insert new stat
                    self.cursor.execute('''
                        INSERT INTO stats (stat_name, stat_value, updated_at)
                        VALUES (?, ?, ?)
                    ''', (stat_name, str(stat_value), timestamp))
            
            self.conn.commit()
            logger.info(f"Successfully saved {len(self.transactions)} transactions to database")
        except sqlite3.Error as e:
            logger.error(f"Database error while saving transactions: {e}")
            self.conn.rollback()
    
    def calculate_stats(self) -> Dict[str, Any]:
        """Calculate statistics from processed transactions.
        
        Returns:
            Dictionary of statistics
        """
        stats = {}
        
        if not self.transactions:
            return stats
            
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(self.transactions)
        
        # Basic stats
        stats['total_transactions'] = len(df)
        stats['total_amount'] = df['amount'].sum()
        stats['avg_transaction_amount'] = df['amount'].mean()
        
        # Transactions by type
        type_counts = df['type'].value_counts().to_dict()
        for type_name, count in type_counts.items():
            stats[f'count_{type_name.lower()}'] = count
        
        # Transactions by category
        category_counts = df['category'].value_counts().to_dict()
        for category, count in category_counts.items():
            stats[f'count_category_{category}'] = count
        
        # Amount by category
        category_amounts = df.groupby('category')['amount'].sum().to_dict()
        for category, amount in category_amounts.items():
            stats[f'amount_category_{category}'] = amount
        
        return stats
    
    def export_to_json(self, output_path: str) -> None:
        """Export processed transactions to JSON for dashboard.
        
        Args:
            output_path: Path to save the JSON file
        """
        if not self.transactions:
            logger.warning("No transactions to export")
            return
            
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Calculate stats
            stats = self.calculate_stats()
            
            # Prepare export data
            export_data = {
                'transactions': self.transactions,
                'stats': stats,
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Write to file
            with open(output_path, 'w') as file:
                json.dump(export_data, file, indent=2)
                
            logger.info(f"Successfully exported data to {output_path}")
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
    
    def process(self) -> None:
        """Process SMS data from XML to database."""
        try:
            # Connect to database
            self.connect_db()
            
            # Read XML data
            messages = self.read_xml()
            if not messages:
                logger.warning("No messages found in XML")
                return
                
            # Process each message
            for message in messages:
                if self.is_momo_sms(message):
                    transaction = self.extract_transaction_details(message)
                    if transaction:
                        self.transactions.append(transaction)
            
            logger.info(f"Processed {len(self.transactions)} MoMo transactions")
            
            # Save to database
            self.save_to_db()
            
            # Export to JSON for dashboard
            json_output_path = os.path.join('data', 'processed', 'dashboard.json')
            self.export_to_json(json_output_path)
            
        except Exception as e:
            logger.error(f"Error in processing: {e}")
        finally:
            # Close database connection
            if self.conn:
                self.conn.close()


def main():
    """Main entry point for the script."""
    try:
        # Get file paths from environment or use defaults
        xml_path = os.environ.get('XML_INPUT_PATH', os.path.join('data', 'raw', 'momo.xml'))
        db_path = os.environ.get('DATABASE_URL', 'mobilemoney.db').replace('sqlite:///', '')
        
        # Check if input file exists
        if not os.path.exists(xml_path):
            logger.error(f"Input file not found: {xml_path}")
            return 1
        
        # Process data
        processor = MomoSmsProcessor(xml_path, db_path)
        processor.process()
        
        logger.info("Processing completed successfully")
        return 0
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())