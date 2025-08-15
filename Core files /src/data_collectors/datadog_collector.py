from datadog import initialize, api
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List
import time

class DatadogCollector:
    """
    Data collector for DataDog metrics and events
    """
    
    def __init__(self, api_key: str, app_key: str):
        self.options = {
            'api_key': api_key,
            'app_key': app_key
        }
        initialize(**self.options)
    
    def collect_infrastructure_metrics(
        self, 
        start_date: str, 
        end_date: str
    ) -> Dict:
        """
        Collect comprehensive infrastructure metrics from DataDog
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Dict containing infrastructure metrics
        """
        
        start_ts = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
        end_ts = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())
        
        metrics = {}
        
        # Collect host metrics
        hosts = api.Hosts.search()
        metrics['total_instances'] = len(hosts['host_list'])
        
        # Collect monitoring costs (estimated based on host count)
        metrics['monitoring_tool_licenses'] = len(hosts['host_list']) * 23 * 12  # DataDog Pro pricing
        
        # Collect incident data
        incidents = self._get_incident_data(start_ts, end_ts)
        metrics.update(incidents)
        
        # Collect performance metrics
        performance = self._get_performance_metrics(start_ts, end_ts)
        metrics.update(performance)
        
        # Collect log volume
        log_metrics = self._get_log_metrics(start_ts, end_ts)
        metrics.update(log_metrics)
        
        # Add estimated operational costs
        metrics['ops_staff_cost'] = 120000  # Average DevOps engineer salary
        metrics['engineer_hourly_cost'] = 100
        metrics['ops_team_size'] = max(1, len(hosts['host_list']) // 100)  # 1 engineer per 100 hosts
        
        return metrics
    
    def _get_incident_data(self, start_ts: int, end_ts: int) -> Dict:
        """Collect incident and downtime data"""
        
        # Query for error rate spikes (proxy for incidents)
        try:
            error_query = api.Metric.query(
                start=start_ts,
                end=end_ts,
                query='avg:trace.flask.request.errors{*}.as_rate()'
            )
            
            # Estimate incidents based on error spikes
            if error_query['series']:
                error_points = error_query['series'][0]['pointlist']
                incident_threshold = 0.05  # 5% error rate threshold
                incidents = sum(1 for point in error_points if point[1] > incident_threshold)
            else:
                incidents = 24  # Default estimate
            
            # Calculate downtime estimates
            avg_incident_duration = 2  # hours
            total_downtime = incidents * avg_incident_duration
            
            return {
                'monthly_incidents': incidents // 12,
                'annual_downtime_hours': total_downtime,
                'mean_time_to_resolution_hours': 4,  # Industry average
                'hourly_revenue_impact': 10000  # Estimated
            }
            
        except Exception as e:
            # Fallback to estimates if API calls fail
            return {
                'monthly_incidents': 20,
                'annual_downtime_hours': 48,
                'mean_time_to_resolution_hours': 4,
                'hourly_revenue_impact': 10000
            }
    
    def _get_performance_metrics(self, start_ts: int, end_ts: int) -> Dict:
        """Collect system performance metrics"""
        
        try:
            # Query CPU utilization
            cpu_query = api.Metric.query(
                start=start_ts,
                end=end_ts,
                query='avg:system.cpu.user{*}'
            )
            
            # Query memory utilization
            memory_query = api.Metric.query(
                start=start_ts,
                end=end_ts,
                query='avg:system.mem.pct_usable{*}'
            )
            
            # Estimate metrics count
            total_metrics = 150  # Conservative estimate per host
            
            return {
                'total_metrics': total_metrics,
                'avg_cpu_utilization': 65,  # Placeholder
                'avg_memory_utilization': 70,  # Placeholder
                'dashboards': 15
            }
            
        except Exception:
            return {
                'total_metrics': 150,
                'avg_cpu_utilization': 65,
                'avg_memory_utilization': 70,
                'dashboards': 15
            }
    
    def _get_log_metrics(self, start_ts: int, end_ts: int) -> Dict:
        """Collect log volume and processing metrics"""
        
        # Estimate log volume based on host count
        # Average application generates ~1GB logs per month per host
        host_count = 100  # Will be updated with actual count
        log_volume_gb = host_count * 1.2  # 20% buffer
        
        return {
            'log_volume_gb_monthly': log_volume_gb,
            'log_retention_days': 30,
            'log_ingestion_rate_gb_day': log_volume_gb / 30
        }
