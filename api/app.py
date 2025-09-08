#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MoMo Data Analysis API

This module provides a FastAPI application that serves MoMo transaction data
for the dashboard frontend.
"""

import os
import sys
import json
import sqlite3
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create FastAPI app
app = FastAPI(
    title="MoMo Data Analysis API",
    description="API for MoMo transaction data analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/web", StaticFiles(directory="web"), name="web")
app.mount("/data", StaticFiles(directory="data"), name="data")

# Database connection
def get_db():
    """Get database connection."""
    # Check for existing database files in order of preference
    db_paths = [
        os.environ.get('DATABASE_URL', '').replace('sqlite:///', ''),
        os.path.join('data', 'processed', 'transactions.db'),
        'mobilemoney.db',
        os.path.join('..', 'mobilemoney.db')
    ]
    
    db_path = None
    for path in db_paths:
        if path and os.path.exists(path):
            db_path = path
            break
    
    # If no database exists, create one with the preferred path
    if not db_path:
        db_path = os.path.join('data', 'processed', 'transactions.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Use check_same_thread=False to avoid threading issues in FastAPI
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    try:
        yield conn
    finally:
        conn.close()


# Models
class Transaction(BaseModel):
    """Transaction model."""
    id: Optional[int] = None
    date: str
    description: str
    amount: float
    type: str
    category: str
    phone: Optional[str] = None
    reference: Optional[str] = None
    processed_date: str


class Stat(BaseModel):
    """Statistic model."""
    stat_name: str
    stat_value: str
    updated_at: str


class DashboardData(BaseModel):
    """Dashboard data model."""
    transactions: List[Transaction]
    stats: Dict[str, Any]
    generated_at: str


# Routes
@app.get("/")
async def root():
    """Serve the main dashboard page."""
    return FileResponse('index.html')

@app.get("/api/", response_model=Dict[str, str])
async def api_root():
    """API root endpoint."""
    return {"message": "MoMo Data Analysis API"}


@app.get("/api/transactions", response_model=List[Transaction])
async def get_transactions(
    conn: sqlite3.Connection = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    type: Optional[str] = None,
    category: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    search: Optional[str] = None
):
    """Get transactions with optional filtering."""
    try:
        query = "SELECT * FROM transactions WHERE 1=1"
        params = []
        
        # Apply filters
        if type:
            query += " AND type = ?"
            params.append(type)
            
        if category:
            query += " AND category = ?"
            params.append(category)
            
        if date_from:
            query += " AND date >= ?"
            params.append(date_from)
            
        if date_to:
            query += " AND date <= ?"
            params.append(date_to)
            
        if search:
            query += " AND (description LIKE ? OR phone LIKE ? OR reference LIKE ?)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])
            
        # Add ordering and pagination
        query += " ORDER BY date DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        # Execute query
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Convert to list of dictionaries
        transactions = [dict(row) for row in rows]
        
        return transactions
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/api/transactions/{transaction_id}", response_model=Transaction)
async def get_transaction(transaction_id: int, conn: sqlite3.Connection = Depends(get_db)):
    """Get a specific transaction by ID."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")
            
        return dict(row)
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/api/stats", response_model=Dict[str, Any])
async def get_stats(conn: sqlite3.Connection = Depends(get_db)):
    """Get all statistics."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM stats")
        rows = cursor.fetchall()
        
        # Convert to dictionary
        stats = {}
        for row in rows:
            row_dict = dict(row)
            stats[row_dict['stat_name']] = row_dict['stat_value']
            
        return stats
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/api/dashboard", response_model=DashboardData)
async def get_dashboard_data(
    conn: sqlite3.Connection = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get all data needed for the dashboard."""
    try:
        # Get transactions
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM transactions ORDER BY date DESC LIMIT ?", 
            (limit,)
        )
        transaction_rows = cursor.fetchall()
        transactions = [dict(row) for row in transaction_rows]
        
        # Get stats
        cursor.execute("SELECT * FROM stats")
        stat_rows = cursor.fetchall()
        stats = {}
        for row in stat_rows:
            row_dict = dict(row)
            # Try to convert to appropriate type
            try:
                value = row_dict['stat_value']
                if value.isdigit():
                    stats[row_dict['stat_name']] = int(value)
                elif value.replace('.', '', 1).isdigit():
                    stats[row_dict['stat_name']] = float(value)
                else:
                    stats[row_dict['stat_name']] = value
            except (ValueError, AttributeError):
                stats[row_dict['stat_name']] = row_dict['stat_value']
        
        # Return dashboard data
        return {
            "transactions": transactions,
            "stats": stats,
            "generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/api/categories")
async def get_categories(conn: sqlite3.Connection = Depends(get_db)):
    """Get all transaction categories with counts."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT category, COUNT(*) as count, SUM(amount) as total_amount 
            FROM transactions 
            GROUP BY category 
            ORDER BY count DESC
        """)
        rows = cursor.fetchall()
        
        categories = [dict(row) for row in rows]
        return categories
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/api/types")
async def get_types(conn: sqlite3.Connection = Depends(get_db)):
    """Get all transaction types with counts."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT type, COUNT(*) as count, SUM(amount) as total_amount 
            FROM transactions 
            GROUP BY type 
            ORDER BY count DESC
        """)
        rows = cursor.fetchall()
        
        types = [dict(row) for row in rows]
        return types
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/api/trends/monthly")
async def get_monthly_trends(
    conn: sqlite3.Connection = Depends(get_db),
    months: int = Query(12, ge=1, le=60)
):
    """Get monthly transaction trends."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                strftime('%Y-%m', date) as month,
                COUNT(*) as count,
                SUM(amount) as total_amount,
                AVG(amount) as avg_amount,
                COUNT(CASE WHEN type = 'CASH_IN' THEN 1 END) as cash_in_count,
                COUNT(CASE WHEN type = 'CASH_OUT' THEN 1 END) as cash_out_count,
                SUM(CASE WHEN type = 'CASH_IN' THEN amount ELSE 0 END) as cash_in_amount,
                SUM(CASE WHEN type = 'CASH_OUT' THEN amount ELSE 0 END) as cash_out_amount
            FROM transactions
            WHERE date >= date('now', ?) 
            GROUP BY month
            ORDER BY month ASC
        """, (f"-{months} months",))
        rows = cursor.fetchall()
        
        trends = [dict(row) for row in rows]
        return trends
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/api/dashboard.json")
async def get_dashboard_json():
    """Get dashboard data from JSON file."""
    try:
        json_path = os.path.join('data', 'processed', 'dashboard.json')
        
        if not os.path.exists(json_path):
            raise HTTPException(status_code=404, detail="Dashboard data not found")
            
        with open(json_path, 'r') as file:
            data = json.load(file)
            
        return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading dashboard data: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    host = os.environ.get('API_HOST', '127.0.0.1')
    port = int(os.environ.get('API_PORT', 8000))
    debug = os.environ.get('API_DEBUG', 'True').lower() in ('true', '1', 't')
    
    uvicorn.run("app:app", host=host, port=port, reload=debug)