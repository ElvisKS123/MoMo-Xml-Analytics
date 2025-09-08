#!/usr/bin/env python
"""
Simple startup script for MoMo Data Analysis Dashboard
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

def main():
    """Start the FastAPI server"""
    print("Starting MoMo Data Analysis Dashboard...")
    print(f"Project root: {project_root}")
    
    # Change to project directory
    os.chdir(project_root)
    
    # Import and run the FastAPI app
    try:
        from api.app import app
        print("FastAPI app imported successfully")
        
        # Start the server
        print("Starting server at http://127.0.0.1:8000")
        print("Dashboard will be available at: http://127.0.0.1:8000")
        uvicorn.run(
            "api.app:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
                                                