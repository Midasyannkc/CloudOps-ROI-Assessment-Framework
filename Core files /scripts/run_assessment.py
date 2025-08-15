#!/usr/bin/env python3
"""
CloudOps ROI Assessment Runner
Usage: python scripts/run_assessment.py --config config/assessment_config.yaml
"""

import argparse
import yaml
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.calculators.roi_calculator import ROICalculator, generate_executive_summary
from src.data_collectors.datadog_collector import DatadogCollector
from src.reports.executive_report import ExecutiveReportGenerator

def main():
    parser = argparse.ArgumentParser(description='Run CloudOps ROI Assessment')
    parser.add_argument('--config', required=True, help='Configuration file path')
    parser.add_argument('--output', default='reports/', help='Output directory')
    
    args = parser.parse_args()
    
    # Load configuration
    with open(args.config, 'r') as file:
        config = yaml.safe_load(file)
    
    print("🚀 Starting CloudOps ROI Assessment...")
    
    # Initialize data collector
    if config['data_source']['type'] == 'datadog':
        collector = DatadogCollector(
            api_key=config['data_source']['api_key'],
            app_key=config['data_source']['app_key']
        )
    else:
        raise ValueError(f"Unsupported data source: {config['data_source']['type']}")
    
    # Collect metrics
    print("📊 Collecting infrastructure metrics...")
    metrics = collector.collect_infrastructure_metrics(
        start_date=config['analysis']['start_date'],
        end_date=config['analysis']['end_date']
    )
    
    # Calculate ROI
    print("💰 Calculating ROI...")
    calculator = ROICalculator()
    roi_results = calculator.calculate_migration_roi(
        current_metrics=metrics,
        target_services=config['aws_services'],
        timeline_months=config['analysis']['timeline_months']
    )
    
    # Generate reports
    print("📋 Generating reports...")
    
    # Executive summary
    summary = generate_executive_summary(roi_results)
    print(summary)
    
    # Save detailed report
    report_generator = ExecutiveReportGenerator()
    report_path = os.path.join(args.output, 'cloudops_roi_assessment.html')
    report_generator.generate_report(roi_results, metrics, report_path)
    
    print(f"✅ Assessment complete! Report saved to {report_path}")
    
    # Print key findings
    print(f"\n🎯 Key Findings:")
    print(f"   • 3-Year ROI: {roi_results['three_year_roi']:.1%}")
    print(f"   • Annual Savings: ${roi_results['annual_savings']:,.0f}")
    print(f"   • Break-even: {roi_results['break_even_months']:.1f} months")

if __name__ == "__main__":
    main()
