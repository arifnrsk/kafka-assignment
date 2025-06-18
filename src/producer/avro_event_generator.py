"""
Avro Event Generator Module
Generates random events compatible with Avro schema for Kafka producer.
"""

import random
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List
import logging


class AvroEventGenerator:
    """Generates random Indonesian events compatible with Avro schema."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        self.event_types = [
            'user_login', 'user_logout', 'purchase', 'add_to_cart',
            'remove_from_cart', 'page_view', 'click', 'form_submit',
            'search', 'api_call', 'error', 'session_timeout'
        ]
        
        self.device_types = ['mobile', 'desktop', 'tablet', 'unknown']
        self.event_statuses = ['success', 'failed', 'pending', 'cancelled']
        self.environments = ['development', 'staging', 'production']
        
        self.indonesian_cities = [
            {'city': 'Jakarta', 'province': 'DKI Jakarta'},
            {'city': 'Surabaya', 'province': 'Jawa Timur'},
            {'city': 'Bandung', 'province': 'Jawa Barat'},
            {'city': 'Medan', 'province': 'Sumatera Utara'},
            {'city': 'Bekasi', 'province': 'Jawa Barat'},
            {'city': 'Tangerang', 'province': 'Banten'},
            {'city': 'Depok', 'province': 'Jawa Barat'},
            {'city': 'Semarang', 'province': 'Jawa Tengah'},
            {'city': 'Palembang', 'province': 'Sumatera Selatan'},
            {'city': 'Makassar', 'province': 'Sulawesi Selatan'}
        ]
        
        self.operating_systems = [
            'Windows 11', 'Windows 10', 'macOS Sonoma', 'Android 14', 'iOS 17'
        ]
        
        self.browsers = [
            'Chrome 120.0', 'Firefox 121.0', 'Safari 17.0', 'Edge 120.0'
        ]
        
        self.product_categories = [
            'Electronics', 'Fashion', 'Books', 'Food & Beverage',
            'Health & Beauty', 'Sports', 'Home & Garden'
        ]
    
    def generate_avro_event(self) -> Dict[str, Any]:
        """Generate a single random event compatible with Avro schema."""
        event_type = random.choice(self.event_types)
        location_data = random.choice(self.indonesian_cities)
        
        timestamp_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        
        event_data = {
            'event_id': str(uuid.uuid4()),
            'event_type': event_type,
            'user_id': str(random.randint(1000, 99999)) if random.random() > 0.1 else None,
            'session_id': str(uuid.uuid4())[:12],
            'timestamp': timestamp_ms,
            'location': {
                'city': location_data['city'],
                'province': location_data['province'],
                'country': 'Indonesia'
            },
            'device_info': {
                'device_type': random.choice(self.device_types),
                'os': random.choice(self.operating_systems) if random.random() > 0.2 else None,
                'browser': random.choice(self.browsers) if random.random() > 0.2 else None
            },
            'event_data': self._generate_event_specific_data(event_type),
            'metadata': {
                'source': 'kafka-producer',
                'version': '1.0.0',
                'environment': random.choice(self.environments)
            }
        }
        
        return event_data
    
    def _generate_event_specific_data(self, event_type: str) -> Dict[str, Any]:
        """Generate event-specific data based on event type."""
        base_data = {
            'value': None,
            'currency': 'IDR',
            'product_id': None,
            'category': None,
            'status': random.choice(self.event_statuses)
        }
        
        if event_type in ['purchase', 'add_to_cart', 'remove_from_cart']:
            base_data.update({
                'value': round(random.uniform(10000, 5000000), 2),
                'product_id': f"PROD_{random.randint(10000, 99999)}",
                'category': random.choice(self.product_categories)
            })
        elif event_type == 'search':
            base_data.update({
                'category': 'Search',
                'value': float(random.randint(1, 1000))
            })
        elif event_type in ['page_view', 'click']:
            base_data.update({
                'category': 'User Interaction',
                'value': float(random.randint(1, 300))
            })
        elif event_type == 'api_call':
            base_data.update({
                'category': 'API',
                'value': float(random.randint(50, 5000))
            })
        elif event_type == 'error':
            base_data.update({
                'category': 'System Error',
                'status': 'failed' if random.random() > 0.3 else random.choice(self.event_statuses)
            })
        
        return base_data
    
    def generate_batch_events(self, count: int) -> List[Dict[str, Any]]:
        """Generate multiple random events."""
        return [self.generate_avro_event() for _ in range(count)]


def create_avro_event_generator() -> AvroEventGenerator:
    """Create an AvroEventGenerator instance."""
    return AvroEventGenerator()


def generate_random_avro_event() -> Dict[str, Any]:
    """Generate a single random Avro-compatible event."""
    generator = create_avro_event_generator()
    return generator.generate_avro_event() 