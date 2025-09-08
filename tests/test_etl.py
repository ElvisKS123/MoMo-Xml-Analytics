#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test ETL process for MoMo Data Analysis
"""

import os
import sys
import unittest
import json
import sqlite3
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

from etl.sms_processor import MomoSmsProcessor

class TestETLProcess(unittest.TestCase):
    """Test the ETL process"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a test processor with test data
        self.test_data_path = project_root / "data" / "raw" / "sample_sms_data.xml"
        self.test_db_path = project_root / "data" / "processed" / "test_transactions.db"
        self.test_json_path = project_root / "data" / "processed" / "test_dashboard_data.json"
        
        # Create test processor
        self.processor = MomoSmsProcessor(
            xml_file=str(self.test_data_path),
            db_file=str(self.test_db_path)
        )
    
    def tearDown(self):
        """Clean up after tests"""
        # Remove test database and output files
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        
        if os.path.exists(self.test_json_path):
            os.remove(self.test_json_path)
    
    def test_xml_parsing(self):
        """Test XML parsing functionality"""
        messages = self.processor.read_xml()
        self.assertIsNotNone(messages)
        self.assertGreater(len(messages), 0)
        
        # Check first message structure
        first_message = messages[0]
        self.assertIn('@id', first_message)
        self.assertIn('@date', first_message)
        self.assertIn('@address', first_message)
        self.assertIn('@body', first_message)
    
    def test_transaction_extraction(self):
        """Test transaction extraction from SMS content"""
        test_message = {
            '@body': "You have received RWF 500000 from JOHN DOE (0244123456) on 01/05/23 at 08:15 AM. Reference: TX123456789. Fee charged: RWF 0. Available Balance: RWF 1250000",
            '@date': '1683014100000',
            '@address': 'MoMo'
        }
        
        transaction = self.processor.extract_transaction_details(test_message)
        
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction['amount'], 500.00)
        self.assertEqual(transaction['type'], 'CASH_IN')
        self.assertIn('phone', transaction)
        self.assertIn('reference', transaction)
    
    def test_categorization(self):
        """Test transaction categorization"""
        # Test cash in categorization
        cash_in = self.processor.categorize_transaction('You have received money from JOHN DOE')
        self.assertIn(cash_in, ['deposit', 'transfer', 'other'])
        
        # Test salary categorization
        salary = self.processor.categorize_transaction('SALARY PAYMENT received')
        self.assertIn(salary, ['salary', 'deposit', 'other'])
        
        # Test bill payment categorization
        bill = self.processor.categorize_transaction('ELECTRICITY BILL payment')
        self.assertIn(bill, ['bills', 'payment', 'other'])
    
    def test_full_etl_process(self):
        """Test the full ETL process"""
        # Skip this test if test data doesn't exist
        if not os.path.exists(self.test_data_path):
            self.skipTest("Test data file not found")
            
        # Run the ETL process
        self.processor.process()
        
        # Check if database was created
        self.assertTrue(os.path.exists(self.test_db_path))
        
        # Check database content
        conn = sqlite3.connect(str(self.test_db_path))
        cursor = conn.cursor()
        
        # Check transactions table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'")
        table_exists = cursor.fetchone()
        self.assertIsNotNone(table_exists)
        
        conn.close()

if __name__ == '__main__':
    unittest.main()