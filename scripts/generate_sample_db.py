#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generate Sample Database

This script creates a sample database with mock transaction data for testing purposes.
"""

import os
import sys
import sqlite3
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def create_sample_transactions(count: int = 100) -> List[Dict[str, Any]]:
    """Create sample transaction data.
    
    Args:
        count: Number of transactions to generate
        
    Returns:
        List of transaction dictionaries
    """
    
    # Sample data
    transaction_types = ['CASH_IN', 'CASH_OUT', 'OTHER']
    categories = ['bills', 'shopping', 'food', 'transport', 'entertainment', 
                  'education', 'health', 'transfer', 'airtime', 'withdrawal', 
                  'deposit', 'salary', 'savings', 'loan', 'other']
    
    sample_descriptions = [
        'MoMo payment received from 0244123456',
        'Withdrew RWF 50000 from agent',
        'Paid bill for electricity',
        'Received salary payment',
        'Sent money to 0201987654',
        'Bought airtime credit',
        'Payment for groceries',
        'Transport fare payment',
        'School fee payment',
        'Medical consultation fee',
        'Shopping at mall',
        'Restaurant payment',
        'Loan repayment',
        'Savings deposit'
    ]
    
    sample_phones = [
        '0244123456', '0201987654', '0209876543', '0244567890',
        '0201234567', '0209123456', '0244987654', '0201567890'
    ]
    
    transactions = []
    
    for i in range(count):
        # Random date in the last 12 months
        days_ago = random.randint(0, 365)
        transaction_date = datetime.now() - timedelta(days=days_ago)
        
        # Random transaction details
        transaction_type = random.choice(transaction_types)
        category = random.choice(categories)
        description = random.choice(sample_descriptions)
        amount = round(random.uniform(5000.0, 1000000.0), 0)
        phone = random.choice(sample_phones) if random.random() > 0.3 else None
        reference = f"REF{random.randint(100000, 999999)}" if random.random() > 0.4 else None
        
        transaction = {
            'date': transaction_date.strftime('%Y-%m-%d %H:%M:%S'),
            'description': description,
            'amount': amount,
            'type': transaction_type,
            'category': category,
            'phone': phone,
            'reference': reference,
            'processed_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        transactions.append(transaction)
    
    return transactions


def create_database_and_insert_data(db_path: str, transactions: List[Dict[str, Any]]) -> None:
    """Create database tables and insert sample data.
    
    Args:
        db_path: Path to SQLite database file
        transactions: List of transaction data to insert
    """
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create transactions table
        cursor.execute('''
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
        
        # Create stats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stat_name TEXT NOT NULL,
                stat_value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Clear existing data
        cursor.execute('DELETE FROM transactions')
        cursor.execute('DELETE FROM stats')
        
        # Insert transaction data
        for transaction in transactions:
            cursor.execute('''
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
        
        # Calculate and insert stats
        stats = calculate_stats(transactions)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        for stat_name, stat_value in stats.items():
            cursor.execute('''
                INSERT INTO stats (stat_name, stat_value, updated_at)
                VALUES (?, ?, ?)
            ''', (stat_name, str(stat_value), timestamp))
        
        conn.commit()
        print(f"Successfully created database with {len(transactions)} transactions")
        
    except Exception as e:
        print(f"Error creating database: {e}")
        conn.rollback()
    finally:
        conn.close()


def calculate_stats(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate statistics from transaction data.
    
    Args:
        transactions: List of transaction data
        
    Returns:
        Dictionary of statistics
    """
    
    stats = {}
    
    if not transactions:
        return stats
    
    # Basic stats
    stats['total_transactions'] = len(transactions)
    stats['total_amount'] = sum(t['amount'] for t in transactions)
    stats['avg_transaction_amount'] = stats['total_amount'] / len(transactions)
    
    # Transaction type counts
    type_counts = {}
    for t in transactions:
        type_counts[t['type']] = type_counts.get(t['type'], 0) + 1
    
    for type_name, count in type_counts.items():
        stats[f'count_{type_name.lower()}'] = count
    
    # Category stats
    category_counts = {}
    category_amounts = {}
    
    for t in transactions:
        category = t['category']
        category_counts[category] = category_counts.get(category, 0) + 1
        category_amounts[category] = category_amounts.get(category, 0) + t['amount']
    
    for category, count in category_counts.items():
        stats[f'count_category_{category}'] = count
        
    for category, amount in category_amounts.items():
        stats[f'amount_category_{category}'] = amount
    
    return stats


def main():
    """Main function to generate sample database."""
    
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate sample database for MoMo Data Analysis')
    parser.add_argument('-n', '--count', type=int, default=100, 
                        help='Number of transactions to generate (default: 100)')
    parser.add_argument('-o', '--output', type=str, default='data/processed/transactions.db',
                        help='Output database path (default: data/processed/transactions.db)')
    
    args = parser.parse_args()
    
    print(f"Generating {args.count} sample transactions...")
    
    # Generate sample data
    transactions = create_sample_transactions(args.count)
    
    # Create database and insert data
    create_database_and_insert_data(args.output, transactions)
    
    print(f"Sample database created at: {args.output}")


if __name__ == '__main__':
    main()
