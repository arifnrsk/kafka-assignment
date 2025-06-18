"""
Event Generator Module
Generates random events for Kafka producer with various data types
"""
import json
import random
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
import numpy as np


@dataclass
class EventData:
    """Event data structure"""
    event_id: str
    timestamp: str
    event_type: str
    user_id: int
    session_id: str
    device_type: str
    location: Dict[str, float]
    metadata: Dict[str, Any]
    value: float
    status: str


class EventGenerator:
    """Generates random events for testing Kafka producer"""
    
    def __init__(self):
        self.event_types = [
            'user_login', 'user_logout', 'page_view', 'purchase', 
            'add_to_cart', 'remove_from_cart', 'search', 'click',
            'form_submit', 'api_call', 'error', 'session_timeout'
        ]
        
        self.device_types = [
            'desktop', 'mobile', 'tablet', 'smart_tv', 'iot_device'
        ]
        
        self.statuses = ['success', 'failed', 'pending', 'cancelled']
        
        self.cities = [
            {'name': 'Jakarta', 'lat': -6.2088, 'lon': 106.8456},
            {'name': 'Surabaya', 'lat': -7.2575, 'lon': 112.7521},
            {'name': 'Bandung', 'lat': -6.9175, 'lon': 107.6191},
            {'name': 'Medan', 'lat': 3.5952, 'lon': 98.6722},
            {'name': 'Bekasi', 'lat': -6.2349, 'lon': 106.9896},
            {'name': 'Tangerang', 'lat': -6.1783, 'lon': 106.6319},
            {'name': 'Depok', 'lat': -6.4025, 'lon': 106.7942}
        ]
    
    def generate_random_event(self) -> EventData:
        """Generate a single random event"""
        city = random.choice(self.cities)
        event_type = random.choice(self.event_types)
        
        event = EventData(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type=event_type,
            user_id=random.randint(1000, 9999),
            session_id=str(uuid.uuid4())[:8],
            device_type=random.choice(self.device_types),
            location={
                'city': city['name'],
                'latitude': city['lat'] + random.uniform(-0.1, 0.1),
                'longitude': city['lon'] + random.uniform(-0.1, 0.1),
                'country': 'Indonesia'
            },
            metadata=self._generate_metadata(event_type),
            value=round(random.uniform(10.0, 1000.0), 2),
            status=random.choice(self.statuses)
        )
        
        return event
    
    def _generate_metadata(self, event_type: str) -> Dict[str, Any]:
        """Generate event-specific metadata"""
        base_metadata = {
            'browser': random.choice(['Chrome', 'Firefox', 'Safari', 'Edge']),
            'os': random.choice(['Windows', 'macOS', 'Linux', 'iOS', 'Android']),
            'ip_address': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            'user_agent': f"Mozilla/5.0 (compatible; KafkaBot/1.0)",
            'referrer': random.choice([
                'https://google.com', 
                'https://facebook.com', 
                'direct', 
                'https://twitter.com'
            ])
        }
        
        # Add event-specific metadata
        if event_type == 'purchase':
            base_metadata.update({
                'product_id': f"PROD_{random.randint(100, 999)}",
                'category': random.choice(['electronics', 'clothing', 'books', 'food']),
                'quantity': random.randint(1, 5),
                'discount': round(random.uniform(0, 30), 2)
            })
        elif event_type == 'search':
            base_metadata.update({
                'query': random.choice([
                    'laptop gaming', 'sepatu olahraga', 'buku programming',
                    'smartphone terbaru', 'tas kerja'
                ]),
                'results_count': random.randint(0, 1000),
                'filter_applied': random.choice([True, False])
            })
        elif event_type == 'page_view':
            base_metadata.update({
                'page_url': f"/page/{random.randint(1, 100)}",
                'page_title': f"Page Title {random.randint(1, 100)}",
                'duration_seconds': random.randint(10, 300)
            })
        elif event_type == 'error':
            base_metadata.update({
                'error_code': random.choice(['404', '500', '403', '400']),
                'error_message': random.choice([
                    'Page not found',
                    'Internal server error',
                    'Access denied', 
                    'Bad request'
                ]),
                'stack_trace': f"Error at line {random.randint(1, 100)}"
            })
        
        return base_metadata
    
    def generate_event_json(self) -> str:
        """Generate random event as JSON string"""
        event = self.generate_random_event()
        return json.dumps(asdict(event), ensure_ascii=False, indent=None)
    
    def generate_batch_events(self, count: int) -> List[EventData]:
        """Generate multiple random events"""
        return [self.generate_random_event() for _ in range(count)]
    
    def generate_batch_events_json(self, count: int) -> List[str]:
        """Generate multiple random events as JSON strings"""
        events = self.generate_batch_events(count)
        return [json.dumps(asdict(event), ensure_ascii=False) for event in events]


# Convenience function for easy import
def create_random_event() -> str:
    """Create a single random event as JSON string"""
    generator = EventGenerator()
    return generator.generate_event_json() 