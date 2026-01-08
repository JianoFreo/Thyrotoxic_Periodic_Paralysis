#!/usr/bin/env python3
"""
TPP Data Generator - Command Line Interface

Generate synthetic TPP monitoring data for testing and development.

Usage:
    python generate_data.py [--output OUTPUT] [--type TYPE] [--records N]
    
Examples:
    python generate_data.py --output synthetic.csv --records 100
    python generate_data.py --type episode --output tpp_episode.json
    python generate_data.py --type daily --records 48
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json
import pandas as pd

# Import from local module
from tpp_utils import SyntheticDataGenerator, save_monitoring_data


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description='Generate synthetic TPP monitoring data.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('-o', '--output', default='synthetic-data.json',
                       help='Output file path (default: synthetic-data.json)')
    parser.add_argument('-t', '--type', choices=['daily', 'episode'], default='daily',
                       help='Type of data to generate (default: daily)')
    parser.add_argument('-n', '--records', type=int, default=48,
                       help='Number of records to generate for daily pattern (default: 48)')
    parser.add_argument('-d', '--duration', type=int, default=120,
                       help='Duration in minutes for episode pattern (default: 120)')
    parser.add_argument('--date', type=str, default=None,
                       help='Start date (YYYY-MM-DD format, default: today)')
    
    args = parser.parse_args()
    
    # Parse start date
    if args.date:
        try:
            start_date = datetime.strptime(args.date, '%Y-%m-%d')
        except ValueError:
            print(f"Error: Invalid date format '{args.date}'. Use YYYY-MM-DD", file=sys.stderr)
            sys.exit(1)
    else:
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Generate data
    generator = SyntheticDataGenerator()
    
    print(f"Generating {args.type} data...", file=sys.stderr)
    
    if args.type == 'daily':
        data = generator.generate_daily_pattern(
            date=start_date,
            num_records=args.records
        )
    else:  # episode
        data = generator.generate_tpp_episode(
            start_time=start_date,
            duration_minutes=args.duration
        )
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    print(f"Generated {len(df)} records", file=sys.stderr)
    print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}", file=sys.stderr)
    
    # Save data
    try:
        save_monitoring_data(df, args.output)
        print(f"Data saved to: {args.output}", file=sys.stderr)
        
        # Print preview
        print("\nPreview (first 5 records):")
        print(df.head().to_string(index=False))
        
    except Exception as e:
        print(f"Error saving data: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
