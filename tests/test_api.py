#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test API functionality for MoMo Data Analysis
"""

import os
import sys
import unittest
import json
from pathlib import Path
from fastapi.testclient import TestClient

# Add project root to path
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

# Import the FastAPI app
from api.app import app

class TestAPIEndpoints(unittest.TestCase):
    """Test the API endpoints"""
    
    def setUp(self):
        """Set up test environment"""
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["message"], "MoMo Data Analysis API")
    
    def test_transactions_endpoint(self):
        """Test the transactions endpoint"""
        response = self.client.get("/transactions")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("items", data)
        self.assertIn("total", data)
        self.assertIn("page", data)
        self.assertIn("size", data)
    
    def test_transactions_filtering(self):
        """Test transactions filtering"""
        # Test type filter
        response = self.client.get("/transactions?type=CASH_IN")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # If there are items, check they all have the correct type
        if data["items"]:
            for item in data["items"]:
                self.assertEqual(item["type"], "CASH_IN")
        
        # Test category filter
        response = self.client.get("/transactions?category=bills")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # If there are items, check they all have the correct category
        if data["items"]:
            for item in data["items"]:
                self.assertEqual(item["category"], "bills")
    
    def test_statistics_endpoint(self):
        """Test the statistics endpoint"""
        response = self.client.get("/statistics")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check for required statistics
        self.assertIn("total_transactions", data)
        self.assertIn("total_amount", data)
        self.assertIn("cash_in_count", data)
        self.assertIn("cash_out_count", data)
    
    def test_dashboard_endpoint(self):
        """Test the dashboard endpoint"""
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check for required dashboard sections
        self.assertIn("transactions", data)
        self.assertIn("statistics", data)
        self.assertIn("charts", data)
    
    def test_categories_endpoint(self):
        """Test the categories endpoint"""
        response = self.client.get("/categories")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check that categories are returned as a list
        self.assertIsInstance(data, list)
        
        # Check for some expected categories
        expected_categories = ["bills", "shopping", "food", "transport"]
        for category in expected_categories:
            self.assertIn(category, data)
    
    def test_types_endpoint(self):
        """Test the types endpoint"""
        response = self.client.get("/types")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check that types are returned as a list
        self.assertIsInstance(data, list)
        
        # Check for expected transaction types
        expected_types = ["CASH_IN", "CASH_OUT", "PAYMENT"]
        for type_ in expected_types:
            self.assertIn(type_, data)
    
    def test_trends_endpoint(self):
        """Test the trends endpoint"""
        response = self.client.get("/trends/monthly")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check that trends data is returned as a list
        self.assertIsInstance(data, list)
        
        # Check structure of trend items if any exist
        if data:
            first_trend = data[0]
            self.assertIn("month", first_trend)
            self.assertIn("year", first_trend)
            self.assertIn("count", first_trend)
            self.assertIn("amount", first_trend)

if __name__ == '__main__':
    unittest.main()