#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Initialize project structure for MoMo Data Analysis
This script creates the necessary directories and files for the project
"""

import os
import sys
import shutil
from pathlib import Path

# Define project structure
PROJECT_STRUCTURE = {
    "api": {
        "__init__.py": "",
        "README.md": "# API Module\n\nThis directory contains the API for the MoMo Data Analysis Dashboard."
    },
    "data": {
        "raw": {},
        "processed": {},
        "logs": {
            "dead_letter": {}
        },
        "README.md": "# Data Directory\n\nThis directory contains the data files for the MoMo Data Analysis Dashboard."
    },
    "etl": {
        "__init__.py": "",
        "README.md": "# ETL Module\n\nThis directory contains the ETL process for the MoMo Data Analysis Dashboard."
    },
    "scripts": {
        "__init__.py": "",
        "README.md": "# Scripts\n\nThis directory contains utility scripts for the MoMo Data Analysis Dashboard."
    },
    "tests": {
        "__init__.py": "",
        "README.md": "# Tests\n\nThis directory contains tests for the MoMo Data Analysis Dashboard."
    },
    "web": {
        "assets": {},
        "README.md": "# Web Frontend\n\nThis directory contains the web frontend for the MoMo Data Analysis Dashboard."
    },
    ".env.example": "# Database Configuration\nDB_PATH=data/processed/transactions.db\n\n# File Paths\nINPUT_PATH=data/raw/sample_sms_data.xml\nOUTPUT_PATH=data/processed/dashboard_data.json\nLOG_PATH=data/logs/etl.log\n\n# API Settings\nAPI_PORT=8000\nAPI_HOST=0.0.0.0\n",
    ".gitignore": "# Python\n__pycache__/\n*.py[cod]\n*$py.class\n\n# Virtual Environment\nvenv/\nenv/\n\n# IDE\n.idea/\n.vscode/\n\n# Logs\nlogs/\n*.log\n\n# Database\n*.db\n*.sqlite3\n\n# Environment variables\n.env\n",
    "requirements.txt": "# Core dependencies\nlxml>=4.9.2\npython-dateutil>=2.8.2\npandas>=1.5.3\nxmltodict>=0.13.0\n\n# Database\nsqlite3>=3.35.0\n\n# API (optional)\nfastapi>=0.95.1\nuvicorn>=0.22.0\npydantic>=1.10.7\n\n# Testing\npytest>=7.3.1\npytest-cov>=4.1.0\n",
    "README.md": "# MoMo Data Analysis Dashboard\n\n## Overview\nA dashboard for analyzing MTN Mobile Money transaction data from SMS messages.\n\n## Installation\n1. Clone this repository\n2. Install dependencies: `pip install -r requirements.txt`\n3. Copy `.env.example` to `.env` and configure\n\n## Usage\nRun the application: `python -m scripts.run`\n\nGenerate sample data: `python -m scripts.generate_sample_data`\n\nRun tests: `python -m scripts.run_tests`\n"
}

def create_directory_structure(base_path, structure):
    """Create directory structure recursively"""
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        
        if isinstance(content, dict):
            # Create directory
            os.makedirs(path, exist_ok=True)
            print(f"Created directory: {path}")
            
            # Recursively create subdirectories and files
            create_directory_structure(path, content)
        else:
            # Create file with content
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Created file: {path}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize project structure for MoMo Data Analysis")
    parser.add_argument(
        "--force", 
        action="store_true", 
        help="Force initialization even if directories already exist"
    )
    
    args = parser.parse_args()
    
    # Get project root directory
    project_root = Path(__file__).parent.parent.absolute()
    
    # Check if project structure already exists
    if not args.force and any(os.path.exists(os.path.join(project_root, d)) for d in ["api", "data", "etl", "web"]):
        print("Project structure already exists. Use --force to reinitialize.")
        return
    
    # Create project structure
    print(f"Initializing project structure in: {project_root}")
    create_directory_structure(project_root, PROJECT_STRUCTURE)
    
    print("\n✅ Project structure initialized successfully!")
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Copy .env.example to .env and configure")
    print("3. Run the application: python -m scripts.run")

if __name__ == "__main__":
    main()