#!/usr/bin/env python3
"""
TPP Data Analyzer - Command Line Interface

Analyze Thyrotoxic Periodic Paralysis monitoring data from the command line.

Usage:
    python analyze_data.py <input_file> [--output OUTPUT] [--format FORMAT]
    
Examples:
    python analyze_data.py sample-data/heart-rate-sample.csv
    python analyze_data.py sample-data/night-monitoring.json --output results.txt
    python analyze_data.py data.csv --format json
"""

import argparse
import json
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime


def load_data(file_path):
    """Load data from CSV or JSON file."""
    path = Path(file_path)
    
    if not path.exists():
        print(f"Error: File '{file_path}' not found.", file=sys.stderr)
        sys.exit(1)
    
    try:
        if path.suffix.lower() == '.csv':
            df = pd.read_csv(file_path)
        elif path.suffix.lower() == '.json':
            with open(file_path, 'r') as f:
                data = json.load(f)
            df = pd.DataFrame(data)
        else:
            print(f"Error: Unsupported file format '{path.suffix}'", file=sys.stderr)
            sys.exit(1)
        
        # Convert timestamp if present
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        return df
    except Exception as e:
        print(f"Error loading file: {e}", file=sys.stderr)
        sys.exit(1)


def analyze_data(df):
    """Perform comprehensive data analysis."""
    results = {
        'summary': {
            'total_records': len(df),
            'columns': list(df.columns),
            'date_range': None
        },
        'statistics': {},
        'anomalies': {},
        'activity_breakdown': {}
    }
    
    # Date range
    if 'timestamp' in df.columns:
        results['summary']['date_range'] = {
            'start': str(df['timestamp'].min()),
            'end': str(df['timestamp'].max()),
            'duration_hours': (df['timestamp'].max() - df['timestamp'].min()).total_seconds() / 3600
        }
    
    # Statistical analysis
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    for col in numeric_columns:
        results['statistics'][col] = {
            'mean': float(df[col].mean()),
            'median': float(df[col].median()),
            'std': float(df[col].std()),
            'min': float(df[col].min()),
            'max': float(df[col].max()),
            'q25': float(df[col].quantile(0.25)),
            'q75': float(df[col].quantile(0.75))
        }
    
    # Anomaly detection (Z-score method)
    if 'heartRate' in df.columns:
        df['hr_zscore'] = np.abs(stats.zscore(df['heartRate']))
        anomaly_threshold = 2.0
        anomalies = df[df['hr_zscore'] > anomaly_threshold]
        
        results['anomalies'] = {
            'count': len(anomalies),
            'percentage': float(len(anomalies) / len(df) * 100),
            'threshold': anomaly_threshold,
            'records': anomalies[['timestamp', 'heartRate', 'hr_zscore']].to_dict('records') if len(anomalies) > 0 else []
        }
    
    # Activity breakdown
    if 'activity' in df.columns:
        activity_counts = df['activity'].value_counts()
        results['activity_breakdown'] = {
            activity: {
                'count': int(count),
                'percentage': float(count / len(df) * 100)
            }
            for activity, count in activity_counts.items()
        }
        
        # Activity-specific stats
        if 'heartRate' in df.columns:
            activity_stats = df.groupby('activity')['heartRate'].agg(['mean', 'std', 'min', 'max'])
            results['activity_stats'] = {
                activity: {
                    'mean_hr': float(row['mean']),
                    'std_hr': float(row['std']),
                    'min_hr': float(row['min']),
                    'max_hr': float(row['max'])
                }
                for activity, row in activity_stats.iterrows()
            }
    
    return results


def format_output(results, output_format='text'):
    """Format analysis results for output."""
    if output_format == 'json':
        return json.dumps(results, indent=2)
    
    # Text format
    lines = []
    lines.append("=" * 60)
    lines.append("TPP DATA ANALYSIS REPORT")
    lines.append("=" * 60)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    # Summary
    lines.append("SUMMARY")
    lines.append("-" * 60)
    lines.append(f"Total Records: {results['summary']['total_records']}")
    lines.append(f"Columns: {', '.join(results['summary']['columns'])}")
    
    if results['summary']['date_range']:
        dr = results['summary']['date_range']
        lines.append(f"Date Range: {dr['start']} to {dr['end']}")
        lines.append(f"Duration: {dr['duration_hours']:.1f} hours")
    lines.append("")
    
    # Statistics
    if results['statistics']:
        lines.append("STATISTICS")
        lines.append("-" * 60)
        for col, stats in results['statistics'].items():
            lines.append(f"{col}:")
            lines.append(f"  Mean: {stats['mean']:.2f}")
            lines.append(f"  Median: {stats['median']:.2f}")
            lines.append(f"  Std Dev: {stats['std']:.2f}")
            lines.append(f"  Range: {stats['min']:.2f} - {stats['max']:.2f}")
            lines.append(f"  IQR: {stats['q25']:.2f} - {stats['q75']:.2f}")
            lines.append("")
    
    # Anomalies
    if results['anomalies']:
        lines.append("ANOMALY DETECTION")
        lines.append("-" * 60)
        lines.append(f"Detected: {results['anomalies']['count']} anomalies ({results['anomalies']['percentage']:.1f}%)")
        lines.append(f"Threshold: Z-score > {results['anomalies']['threshold']}")
        lines.append("")
    
    # Activity breakdown
    if results['activity_breakdown']:
        lines.append("ACTIVITY BREAKDOWN")
        lines.append("-" * 60)
        for activity, info in results['activity_breakdown'].items():
            lines.append(f"{activity}: {info['count']} records ({info['percentage']:.1f}%)")
        lines.append("")
    
    # Activity stats
    if 'activity_stats' in results:
        lines.append("ACTIVITY-SPECIFIC HEART RATE")
        lines.append("-" * 60)
        for activity, stats in results['activity_stats'].items():
            lines.append(f"{activity}:")
            lines.append(f"  Mean: {stats['mean_hr']:.1f} bpm")
            lines.append(f"  Std: {stats['std_hr']:.1f} bpm")
            lines.append(f"  Range: {stats['min_hr']:.1f} - {stats['max_hr']:.1f} bpm")
        lines.append("")
    
    lines.append("=" * 60)
    return "\n".join(lines)


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description='Analyze TPP monitoring data from CSV or JSON files.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('input_file', help='Input data file (CSV or JSON)')
    parser.add_argument('-o', '--output', help='Output file (default: print to stdout)')
    parser.add_argument('-f', '--format', choices=['text', 'json'], default='text',
                       help='Output format (default: text)')
    
    args = parser.parse_args()
    
    # Load and analyze data
    print(f"Loading data from {args.input_file}...", file=sys.stderr)
    df = load_data(args.input_file)
    
    print(f"Analyzing {len(df)} records...", file=sys.stderr)
    results = analyze_data(df)
    
    # Format output
    output = format_output(results, args.format)
    
    # Write output
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(output)
        print(f"Results written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == '__main__':
    main()
