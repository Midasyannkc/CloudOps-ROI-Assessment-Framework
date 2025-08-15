import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import yaml

class ROICalculator:
    """
    Main ROI calculator for CloudOps migration assessment
    """
    
    def __init__(self, config_path: str = "config/cost_models.yaml"):
        with open(config_path, 'r') as file:
            self.cost_models = yaml.safe_load(file)
        
        self.aws_pricing = {
            'cloudwatch': {
                'metrics': 0.30,  # per metric per month
                'logs_ingestion': 0.50,  # per GB
                'dashboard': 3.00  # per dashboard per month
            },
            'systems_manager': {
                'patch_management': 0.09,  # per instance per month
                'inventory': 0.0033,  # per instance per month
                'automation': 0.02  # per automation execution
            },
            'config': {
                'configuration_items': 0.003,  # per configuration item
                'rules': 0.001  # per rule evaluation
            }
        }
    
    def calculate_migration_roi(
        self, 
        current_metrics: Dict, 
        target_services: List[str],
        timeline_months: int = 36
    ) -> Dict:
        """
        Calculate comprehensive ROI for CloudOps migration
        
        Args:
            current_metrics: Current infrastructure metrics
            target_services: AWS services to migrate to
            timeline_months: Analysis timeline in months
            
        Returns:
            Dict containing ROI analysis results
        """
        
        # Calculate current costs
        current_annual_cost = self._calculate_current_costs(current_metrics)
        
        # Calculate AWS projected costs
        aws_annual_cost = self._calculate_aws_costs(current_metrics, target_services)
        
        # Calculate operational savings
        operational_savings = self._calculate_operational_savings(current_metrics)
        
        # Calculate risk mitigation value
        risk_mitigation = self._calculate_risk_mitigation(current_metrics)
        
        # Calculate migration costs
        migration_cost = self._calculate_migration_costs(current_metrics, target_services)
        
        # Perform ROI analysis
        annual_savings = (current_annual_cost - aws_annual_cost + 
                         operational_savings + risk_mitigation)
        
        three_year_savings = annual_savings * 3
        three_year_roi = (three_year_savings - migration_cost) / migration_cost
        
        break_even_months = migration_cost / (annual_savings / 12) if annual_savings > 0 else float('inf')
        
        return {
            'current_annual_cost': current_annual_cost,
            'aws_annual_cost': aws_annual_cost,
            'annual_savings': annual_savings,
            'three_year_savings': three_year_savings,
            'migration_cost': migration_cost,
            'three_year_roi': three_year_roi,
            'break_even_months': break_even_months,
            'operational_savings': operational_savings,
            'risk_mitigation_value': risk_mitigation,
            'cost_breakdown': {
                'infrastructure_savings': current_annual_cost - aws_annual_cost,
                'productivity_gains': operational_savings,
                'risk_reduction': risk_mitigation
            }
        }
    
    def _calculate_current_costs(self, metrics: Dict) -> float:
        """Calculate current infrastructure operational costs"""
        base_costs = {
            'monitoring_tools': metrics.get('monitoring_tool_licenses', 0),
            'infrastructure': metrics.get('server_costs', 0),
            'staff_overhead': metrics.get('ops_staff_cost', 0) * 0.3,  # 30% time on monitoring
            'downtime_cost': metrics.get('annual_downtime_hours', 0) * 
                           metrics.get('hourly_revenue_impact', 0)
        }
        return sum(base_costs.values())
    
    def _calculate_aws_costs(self, metrics: Dict, services: List[str]) -> float:
        """Calculate projected AWS service costs"""
        total_cost = 0
        
        if 'cloudwatch' in services:
            metrics_count = metrics.get('total_metrics', 100)
            log_volume_gb = metrics.get('log_volume_gb_monthly', 50)
            dashboards = metrics.get('dashboards', 10)
            
            total_cost += (
                metrics_count * self.aws_pricing['cloudwatch']['metrics'] * 12 +
                log_volume_gb * self.aws_pricing['cloudwatch']['logs_ingestion'] * 12 +
                dashboards * self.aws_pricing['cloudwatch']['dashboard'] * 12
            )
        
        if 'systems_manager' in services:
            instances = metrics.get('total_instances', 100)
            automations = metrics.get('monthly_automations', 50)
            
            total_cost += (
                instances * self.aws_pricing['systems_manager']['patch_management'] * 12 +
                instances * self.aws_pricing['systems_manager']['inventory'] * 12 +
                automations * self.aws_pricing['systems_manager']['automation'] * 12
            )
        
        if 'config' in services:
            config_items = metrics.get('configuration_items', 500)
            rule_evaluations = metrics.get('compliance_checks_monthly', 1000)
            
            total_cost += (
                config_items * self.aws_pricing['config']['configuration_items'] * 12 +
                rule_evaluations * self.aws_pricing['config']['rules'] * 12
            )
        
        return total_cost
    
    def _calculate_operational_savings(self, metrics: Dict) -> float:
        """Calculate operational efficiency improvements"""
        current_mttr = metrics.get('mean_time_to_resolution_hours', 4)
        projected_mttr = current_mttr * 0.4  # 60% improvement
        
        incident_frequency = metrics.get('monthly_incidents', 20)
        avg_engineer_cost_per_hour = metrics.get('engineer_hourly_cost', 100)
        
        monthly_savings = (
            incident_frequency * 
            (current_mttr - projected_mttr) * 
            avg_engineer_cost_per_hour
        )
        
        return monthly_savings * 12
    
    def _calculate_risk_mitigation(self, metrics: Dict) -> float:
        """Calculate value of risk mitigation"""
        # Compliance risk reduction
        compliance_violations = metrics.get('annual_compliance_violations', 2)
        avg_violation_cost = metrics.get('compliance_violation_cost', 50000)
        compliance_improvement = 0.8  # 80% reduction
        
        # Security incident prevention
        security_incidents = metrics.get('annual_security_incidents', 1)
        avg_security_cost = metrics.get('security_incident_cost', 100000)
        security_improvement = 0.7  # 70% reduction
        
        return (
            compliance_violations * avg_violation_cost * compliance_improvement +
            security_incidents * avg_security_cost * security_improvement
        )
    
    def _calculate_migration_costs(self, metrics: Dict, services: List[str]) -> float:
        """Calculate one-time migration costs"""
        base_migration_cost = 50000  # Base implementation cost
        
        # Scale based on complexity
        complexity_multiplier = 1.0
        if metrics.get('total_instances', 0) > 500:
            complexity_multiplier *= 1.5
        if len(services) > 2:
            complexity_multiplier *= 1.2
        
        # Training costs
        training_cost = metrics.get('ops_team_size', 5) * 2000  # $2k per person
        
        return base_migration_cost * complexity_multiplier + training_cost

def generate_executive_summary(roi_data: Dict) -> str:
    """Generate executive summary of ROI analysis"""
    
    summary = f"""
    CloudOps Migration ROI Executive Summary
    ========================================
    
    Financial Impact:
    • Annual Cost Savings: ${roi_data['annual_savings']:,.0f}
    • 3-Year ROI: {roi_data['three_year_roi']:.1%}
    • Break-even Point: {roi_data['break_even_months']:.1f} months
    • Migration Investment: ${roi_data['migration_cost']:,.0f}
    
    Key Benefits:
    • Infrastructure Cost Reduction: ${roi_data['cost_breakdown']['infrastructure_savings']:,.0f}/year
    • Operational Efficiency Gains: ${roi_data['cost_breakdown']['productivity_gains']:,.0f}/year
    • Risk Mitigation Value: ${roi_data['cost_breakdown']['risk_reduction']:,.0f}/year
    
    Business Case: {"STRONG" if roi_data['three_year_roi'] > 1.0 else "MODERATE" if roi_data['three_year_roi'] > 0.3 else "WEAK"}
    """
    
    return summary
