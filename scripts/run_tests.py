#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Run tests for MoMo Data Analysis
This script runs all tests or specific test modules
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

def run_tests(test_path=None, verbose=False, coverage=False):
    """Run tests with pytest"""
    print("\n===== Running Tests =====\n")
    
    # Build command
    cmd = [sys.executable, "-m", "pytest"]
    
    # Add options
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=etl", "--cov=api", "--cov-report=term"])
    
    # Add test path if specified
    if test_path:
        test_path = os.path.join(project_root, test_path)
        cmd.append(test_path)
    else:
        cmd.append(os.path.join(project_root, "tests"))
    
    # Run tests
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ Tests completed successfully!\n")
        return True
    except subprocess.CalledProcessError:
        print("\n❌ Some tests failed!\n")
        return False
    except Exception as e:
        print(f"\n❌ Error running tests: {e}\n")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Run tests for MoMo Data Analysis")
    parser.add_argument(
        "--test-path", 
        type=str, 
        help="Specific test file or directory to run"
    )
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true", 
        help="Run tests with verbose output"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true", 
        help="Generate test coverage report"
    )
    
    args = parser.parse_args()
    
    # Run tests
    success = run_tests(
        test_path=args.test_path,
        verbose=args.verbose,
        coverage=args.coverage
    )
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()