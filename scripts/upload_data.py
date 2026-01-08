#!/usr/bin/env python3
"""
TPP Data Uploader - Command Line Interface

Upload monitoring data to the TPP backend API from the command line.

Usage:
    python upload_data.py <input_file> [--url URL] [--verbose]
    
Examples:
    python upload_data.py sample-data/heart-rate-sample.csv
    python upload_data.py data.json --url http://localhost:3000
    python upload_data.py data.csv --verbose
"""

import argparse
import json
import sys
from pathlib import Path
import requests
from datetime import datetime


DEFAULT_API_URL = "http://localhost:3000"


def upload_file(file_path, api_url, verbose=False):
    """Upload a file to the TPP backend API."""
    path = Path(file_path)
    
    if not path.exists():
        print(f"Error: File '{file_path}' not found.", file=sys.stderr)
        return False
    
    upload_endpoint = f"{api_url}/upload"
    
    try:
        # Determine content type
        if path.suffix.lower() == '.csv':
            content_type = 'text/csv'
        elif path.suffix.lower() == '.json':
            content_type = 'application/json'
        else:
            print(f"Warning: Unknown file type '{path.suffix}', attempting upload anyway...")
            content_type = 'application/octet-stream'
        
        # Read file content
        with open(path, 'rb') as f:
            file_content = f.read()
        
        # Prepare multipart form data
        files = {
            'file': (path.name, file_content, content_type)
        }
        
        if verbose:
            print(f"Uploading {path.name} ({len(file_content)} bytes) to {upload_endpoint}...")
        
        # Send request
        response = requests.post(upload_endpoint, files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Upload successful!")
            print(f"   File: {path.name}")
            print(f"   Records: {result.get('count', 'N/A')}")
            print(f"   Message: {result.get('message', 'N/A')}")
            
            if verbose:
                print(f"   Response: {json.dumps(result, indent=2)}")
            
            return True
        else:
            print(f"❌ Upload failed with status {response.status_code}", file=sys.stderr)
            print(f"   Response: {response.text}", file=sys.stderr)
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to server at {api_url}", file=sys.stderr)
        print(f"   Make sure the backend is running: npm start", file=sys.stderr)
        return False
    except Exception as e:
        print(f"❌ Error during upload: {e}", file=sys.stderr)
        return False


def check_server_health(api_url, verbose=False):
    """Check if the backend server is healthy."""
    health_endpoint = f"{api_url}/health"
    
    try:
        if verbose:
            print(f"Checking server health at {health_endpoint}...")
        
        response = requests.get(health_endpoint, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if verbose:
                print(f"✅ Server is healthy!")
                print(f"   Status: {data.get('status')}")
                print(f"   Message: {data.get('message')}")
            return True
        else:
            print(f"⚠️  Server returned status {response.status_code}", file=sys.stderr)
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to server at {api_url}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"❌ Health check failed: {e}", file=sys.stderr)
        return False


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description='Upload TPP monitoring data to the backend API.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('input_file', help='Input data file to upload (CSV or JSON)')
    parser.add_argument('-u', '--url', default=DEFAULT_API_URL,
                       help=f'Backend API URL (default: {DEFAULT_API_URL})')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose output')
    parser.add_argument('--skip-health-check', action='store_true',
                       help='Skip server health check before upload')
    
    args = parser.parse_args()
    
    # Health check
    if not args.skip_health_check:
        if not check_server_health(args.url, args.verbose):
            print("\nServer health check failed. Use --skip-health-check to bypass.", file=sys.stderr)
            sys.exit(1)
        if args.verbose:
            print()
    
    # Upload file
    success = upload_file(args.input_file, args.url, args.verbose)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
