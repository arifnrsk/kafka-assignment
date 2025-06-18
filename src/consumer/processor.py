"""
Event Processor Module
Processes consumed events and performs calculations
"""
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from dataclasses import dataclass
import statistics
from collections import defaultdict, Counter

from utils import processor_logger


@dataclass
class ProcessingResult:
    """Result of event processing"""
    event_id: str
    processed_at: str
    calculations: Dict[str, Any]
    summary: str
    alerts: List[str]


class EventProcessor:
    """Processes events and performs various calculations"""
    
    def __init__(self):
        self.logger = processor_logger
        self.processed_events: List[Dict[str, Any]] = []
        self.processing_stats = {
            'total_processed': 0,
            'processing_errors': 0,
            'event_types': Counter(),
            'user_activities': defaultdict(int),
            'location_stats': Counter(),
            'device_stats': Counter(),
            'hourly_stats': defaultdict(int),
            'total_values': [],
            'status_counts': Counter()
        }
    
    def process_event(self, event_data) -> Optional[ProcessingResult]:
        """Process a single event and perform calculations"""
        try:
            # Handle both JSON string and dict formats
            if isinstance(event_data, str):
                event = json.loads(event_data)
            elif isinstance(event_data, dict):
                event = event_data
            else:
                raise ValueError(f"Unsupported event data type: {type(event_data)}")
            
            # Update statistics
            self._update_statistics(event)
            
            # Perform calculations
            calculations = self._perform_calculations(event)
            
            # Generate summary
            summary = self._generate_summary(event, calculations)
            
            # Check for alerts
            alerts = self._check_alerts(event, calculations)
            
            # Create result
            result = ProcessingResult(
                event_id=event.get('event_id', 'unknown'),
                processed_at=datetime.now(timezone.utc).isoformat(),
                calculations=calculations,
                summary=summary,
                alerts=alerts
            )
            
            # Store event for batch processing
            self.processed_events.append(event)
            self.processing_stats['total_processed'] += 1
            
            self.logger.info(f"Processed event {event.get('event_id', 'unknown')[:8]}...")
            
            if alerts:
                for alert in alerts:
                    self.logger.warning(f"WARNING: {alert}")
            
            return result
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in event data: {str(e)}")
            self.processing_stats['processing_errors'] += 1
            return None
        except Exception as e:
            self.logger.error(f"Error processing event: {str(e)}")
            self.processing_stats['processing_errors'] += 1
            return None
    
    def _update_statistics(self, event: Dict[str, Any]):
        """Update internal statistics with event data"""
        # Event type statistics
        event_type = event.get('event_type', 'unknown')
        self.processing_stats['event_types'][event_type] += 1
        
        # User activity statistics
        user_id = event.get('user_id')
        if user_id:
            self.processing_stats['user_activities'][user_id] += 1
        
        # Location statistics
        location = event.get('location', {})
        if location.get('city'):
            self.processing_stats['location_stats'][location['city']] += 1
        
        # Device statistics
        device_type = event.get('device_type', 'unknown')
        self.processing_stats['device_stats'][device_type] += 1
        
        # Hourly statistics
        timestamp = event.get('timestamp', '')
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                hour = dt.hour
                self.processing_stats['hourly_stats'][hour] += 1
            except:
                pass
        
        # Value statistics
        value = event.get('value')
        if value and isinstance(value, (int, float)):
            self.processing_stats['total_values'].append(value)
        
        # Status statistics
        status = event.get('status', 'unknown')
        self.processing_stats['status_counts'][status] += 1
    
    def _perform_calculations(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Perform various calculations on the event"""
        calculations = {}
        
        # Basic event calculations
        calculations['event_age_seconds'] = self._calculate_event_age(event)
        calculations['value_category'] = self._categorize_value(event.get('value', 0))
        calculations['risk_score'] = self._calculate_risk_score(event)
        
        # User behavior calculations
        user_id = event.get('user_id')
        if user_id:
            calculations['user_activity_count'] = self.processing_stats['user_activities'][user_id]
            calculations['user_activity_level'] = self._categorize_user_activity(
                self.processing_stats['user_activities'][user_id]
            )
        
        # Location calculations
        location = event.get('location', {})
        if location:
            calculations['location_popularity'] = self._calculate_location_popularity(location)
        
        # Metadata analysis
        metadata = event.get('metadata', {})
        calculations['metadata_richness'] = len(metadata)
        calculations['has_error_indicators'] = self._has_error_indicators(event)
        
        # Statistical calculations (if we have enough data)
        if len(self.processing_stats['total_values']) > 1:
            calculations['value_vs_avg'] = self._compare_to_average(event.get('value', 0))
            calculations['value_percentile'] = self._calculate_percentile(event.get('value', 0))
        
        return calculations
    
    def _calculate_event_age(self, event: Dict[str, Any]) -> Optional[float]:
        """Calculate how old the event is in seconds"""
        try:
            timestamp_str = event.get('timestamp', '')
            if not timestamp_str:
                return None
            
            event_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            age_seconds = (now - event_time).total_seconds()
            
            return round(age_seconds, 2)
        except:
            return None
    
    def _categorize_value(self, value: float) -> str:
        """Categorize event value into ranges"""
        if value < 50:
            return 'low'
        elif value < 200:
            return 'medium'
        elif value < 500:
            return 'high'
        else:
            return 'very_high'
    
    def _calculate_risk_score(self, event: Dict[str, Any]) -> float:
        """Calculate risk score based on event characteristics"""
        risk_score = 0.0
        
        # High values are riskier
        value = event.get('value', 0)
        if value > 500:
            risk_score += 0.3
        elif value > 200:
            risk_score += 0.1
        
        # Failed events are riskier
        if event.get('status') == 'failed':
            risk_score += 0.4
        
        # Error events are very risky
        if event.get('event_type') == 'error':
            risk_score += 0.5
        
        # Night time events (outside business hours) are riskier
        try:
            timestamp_str = event.get('timestamp', '')
            if timestamp_str:
                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                hour = dt.hour
                if hour < 6 or hour > 22:  # Outside business hours
                    risk_score += 0.2
        except:
            pass
        
        # Metadata anomalies
        metadata = event.get('metadata', {})
        if metadata.get('error_code'):
            risk_score += 0.3
        
        return min(risk_score, 1.0)  # Cap at 1.0
    
    def _categorize_user_activity(self, activity_count: int) -> str:
        """Categorize user activity level"""
        if activity_count <= 2:
            return 'low'
        elif activity_count <= 5:
            return 'medium'
        elif activity_count <= 10:
            return 'high'
        else:
            return 'very_high'
    
    def _calculate_location_popularity(self, location: Dict[str, Any]) -> str:
        """Calculate location popularity based on stats"""
        city = location.get('city', '')
        if not city:
            return 'unknown'
        
        city_count = self.processing_stats['location_stats'][city]
        total_events = sum(self.processing_stats['location_stats'].values())
        
        if total_events == 0:
            return 'unknown'
        
        popularity_ratio = city_count / total_events
        
        if popularity_ratio > 0.3:
            return 'very_popular'
        elif popularity_ratio > 0.15:
            return 'popular'
        elif popularity_ratio > 0.05:
            return 'moderate'
        else:
            return 'rare'
    
    def _has_error_indicators(self, event: Dict[str, Any]) -> bool:
        """Check if event has error indicators"""
        # Check event type
        if event.get('event_type') == 'error':
            return True
        
        # Check status
        if event.get('status') in ['failed', 'cancelled']:
            return True
        
        # Check metadata for error codes
        metadata = event.get('metadata', {})
        if metadata.get('error_code') or metadata.get('error_message'):
            return True
        
        return False
    
    def _compare_to_average(self, value: float) -> str:
        """Compare value to running average"""
        if not self.processing_stats['total_values']:
            return 'no_data'
        
        avg_value = statistics.mean(self.processing_stats['total_values'])
        
        if value > avg_value * 1.5:
            return 'much_higher'
        elif value > avg_value * 1.1:
            return 'higher'
        elif value < avg_value * 0.5:
            return 'much_lower'
        elif value < avg_value * 0.9:
            return 'lower'
        else:
            return 'similar'
    
    def _calculate_percentile(self, value: float) -> Optional[float]:
        """Calculate percentile of value in dataset"""
        if len(self.processing_stats['total_values']) < 2:
            return None
        
        sorted_values = sorted(self.processing_stats['total_values'])
        position = sum(1 for v in sorted_values if v <= value)
        percentile = (position / len(sorted_values)) * 100
        
        return round(percentile, 1)
    
    def _generate_summary(self, event: Dict[str, Any], calculations: Dict[str, Any]) -> str:
        """Generate human-readable summary of processing"""
        event_type = event.get('event_type', 'unknown')
        user_id = event.get('user_id', 'unknown')
        value = event.get('value', 0)
        status = event.get('status', 'unknown')
        
        summary = f"Processed {event_type} event from user {user_id} "
        summary += f"with value ${value} ({status}). "
        
        if calculations.get('risk_score', 0) > 0.5:
            summary += "HIGH RISK event detected. "
        
        if calculations.get('value_category') == 'very_high':
            summary += "Very high value transaction. "
        
        return summary
    
    def _check_alerts(self, event: Dict[str, Any], calculations: Dict[str, Any]) -> List[str]:
        """Check for conditions that should generate alerts"""
        alerts = []
        
        # High risk score alert
        risk_score = calculations.get('risk_score', 0)
        if risk_score > 0.7:
            alerts.append(f"High risk score: {risk_score:.2f}")
        
        # High value alert
        value = event.get('value', 0)
        if value > 800:
            alerts.append(f"High value transaction: ${value}")
        
        # Error event alert
        if event.get('event_type') == 'error':
            alerts.append("Error event detected")
        
        # Failed status alert
        if event.get('status') == 'failed':
            alerts.append("Failed event status")
        
        # Suspicious user activity
        user_activity = calculations.get('user_activity_count', 0)
        if user_activity > 15:
            alerts.append(f"High user activity: {user_activity} events")
        
        return alerts
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """Get summary of all processing statistics"""
        summary = dict(self.processing_stats)
        
        # Calculate derived statistics
        if self.processing_stats['total_values']:
            summary['value_statistics'] = {
                'mean': round(statistics.mean(self.processing_stats['total_values']), 2),
                'median': round(statistics.median(self.processing_stats['total_values']), 2),
                'min': round(min(self.processing_stats['total_values']), 2),
                'max': round(max(self.processing_stats['total_values']), 2),
                'count': len(self.processing_stats['total_values'])
            }
        
        # Top categories
        summary['top_event_types'] = dict(self.processing_stats['event_types'].most_common(5))
        summary['top_locations'] = dict(self.processing_stats['location_stats'].most_common(5))
        summary['top_devices'] = dict(self.processing_stats['device_stats'].most_common(5))
        
        return summary 