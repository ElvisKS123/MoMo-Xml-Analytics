#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Run script for MoMo Data Analysis
This script runs the ETL process and starts the API server
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

def run_etl():
    """Run the ETL process"""
    print("\n===== Running ETL Process =====\n")
    try:
        from etl.sms_processor import MomoSmsProcessor
        import os
        
        # Get file paths from environment or use defaults
        xml_path = os.environ.get('XML_INPUT_PATH', os.path.join('data', 'raw', 'momo.xml'))
        db_path = os.environ.get('DATABASE_URL', 'data/processed/transactions.db').replace('sqlite:///', '')
        
        processor = MomoSmsProcessor(xml_path, db_path)
        processor.process()
        print("\n[SUCCESS] ETL process completed successfully!\n")
        return True
    except Exception as e:
        print(f"\n[ERROR] Error running ETL process: {e}\n")
        return False

def run_api(port=8000):
    """Start the API server"""
    print(f"\n===== Starting API Server on port {port} =====\n")
    api_path = project_root / "api" / "app.py"
    
    try:
        # Use uvicorn to run the FastAPI app
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "api.app:app", 
            "--reload", 
            f"--port={port}", 
            "--host=0.0.0.0"
        ]
        
        # Run the API server
        api_process = subprocess.Popen(
            cmd,
            cwd=str(project_root)
        )
        
        print(f"\n[SUCCESS] API server started successfully!")
        print(f"[INFO] Dashboard available at: http://localhost:{port}")
        print("\nPress Ctrl+C to stop the server...\n")
        
        # Keep the script running
        api_process.wait()
        
    except KeyboardInterrupt:
        print("\n\n[INFO] Stopping API server...")
        return True
    except Exception as e:
        print(f"\n[ERROR] Error starting API server: {e}\n")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="MoMo Data Analysis Runner")
    parser.add_argument(
        "--skip-etl", 
        action="store_true", 
        help="Skip the ETL process"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="Port for the API server"
    )
    
    args = parser.parse_args()
    
    # Run ETL process if not skipped
    if not args.skip_etl:
        etl_success = run_etl()
        if not etl_success:
            print("\n[WARNING] ETL process failed. Starting API server anyway...\n")
    else:
        print("\n[INFO] Skipping ETL process as requested\n")
    
    # Start API server
    run_api(port=args.port)

if __name__ == "__main__":
    main()