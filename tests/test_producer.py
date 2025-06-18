"""
Unit tests for Kafka Producer components
"""
import pytest
import json
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from producer.event_generator import EventGenerator, EventData, create_random_event
from producer.event_producer import KafkaEventProducer


class TestEventGenerator:
    """Test cases for EventGenerator"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.generator = EventGenerator()
    
    def test_generate_random_event(self):
        """Test random event generation"""
        event = self.generator.generate_random_event()
        
        # Check that event is an EventData instance
        assert isinstance(event, EventData)
        
        # Check required fields
        assert event.event_id is not None
        assert event.timestamp is not None
        assert event.event_type in self.generator.event_types
        assert isinstance(event.user_id, int)
        assert event.user_id >= 1000 and event.user_id <= 9999
        assert event.device_type in self.generator.device_types
        assert event.status in self.generator.statuses
        
        # Check location structure
        assert isinstance(event.location, dict)
        assert 'city' in event.location
        assert 'latitude' in event.location
        assert 'longitude' in event.location
        assert 'country' in event.location
        assert event.location['country'] == 'Indonesia'
        
        # Check metadata structure
        assert isinstance(event.metadata, dict)
        assert 'browser' in event.metadata
        assert 'os' in event.metadata
        assert 'ip_address' in event.metadata
        
        # Check value range
        assert isinstance(event.value, float)
        assert event.value >= 10.0 and event.value <= 1000.0
    
    def test_generate_event_json(self):
        """Test JSON event generation"""
        event_json = self.generator.generate_event_json()
        
        # Check that it's valid JSON
        event_data = json.loads(event_json)
        
        # Check JSON structure
        assert 'event_id' in event_data
        assert 'timestamp' in event_data
        assert 'event_type' in event_data
        assert 'user_id' in event_data
        assert 'location' in event_data
        assert 'metadata' in event_data
        assert 'value' in event_data
        assert 'status' in event_data
    
    def test_generate_batch_events(self):
        """Test batch event generation"""
        batch_size = 5
        events = self.generator.generate_batch_events(batch_size)
        
        assert len(events) == batch_size
        assert all(isinstance(event, EventData) for event in events)
        
        # Check that events are different
        event_ids = [event.event_id for event in events]
        assert len(set(event_ids)) == batch_size  # All unique
    
    def test_generate_batch_events_json(self):
        """Test batch JSON event generation"""
        batch_size = 3
        events_json = self.generator.generate_batch_events_json(batch_size)
        
        assert len(events_json) == batch_size
        
        # Verify each is valid JSON
        for event_json in events_json:
            event_data = json.loads(event_json)
            assert 'event_id' in event_data
    
    def test_event_specific_metadata(self):
        """Test event-specific metadata generation"""
        # Test purchase event metadata
        purchase_event = None
        for _ in range(50):  # Try multiple times to get a purchase event
            event = self.generator.generate_random_event()
            if event.event_type == 'purchase':
                purchase_event = event
                break
        
        if purchase_event:
            metadata = purchase_event.metadata
            assert 'product_id' in metadata
            assert 'category' in metadata
            assert 'quantity' in metadata
    
    def test_create_random_event_function(self):
        """Test convenience function"""
        event_json = create_random_event()
        
        # Should be valid JSON
        event_data = json.loads(event_json)
        assert 'event_id' in event_data


class TestKafkaEventProducer:
    """Test cases for KafkaEventProducer"""
    
    def setup_method(self):
        """Setup test fixtures"""  
        # Note: These tests don't actually connect to Kafka
        # They test the class structure and configuration
        pass
    
    def test_producer_initialization(self):
        """Test producer initialization"""
        producer = KafkaEventProducer()
        
        assert producer.config_manager is not None
        assert producer.logger is not None
        assert producer.event_generator is not None
        assert producer.producer is None  # Not connected yet
        assert producer.running is False
        assert producer.total_messages_sent == 0
        assert producer.failed_messages == 0
    
    def test_signal_handler(self):
        """Test signal handler setup"""
        producer = KafkaEventProducer()
        
        # Simulate signal
        producer._signal_handler(2, None)  # SIGINT
        assert producer.running is False


if __name__ == "__main__":
    # Run basic tests
    print("Running Producer Tests...")
    
    # Test EventGenerator
    print("\nTesting EventGenerator...")
    generator = EventGenerator()
    
    # Generate a few events
    for i in range(3):
        event = generator.generate_random_event()
        print(f"   Event {i+1}: {event.event_type} by user {event.user_id}")
    
    # Test JSON generation
    print("\nTesting JSON generation...")
    event_json = create_random_event()
    event_data = json.loads(event_json)
    print(f"   Generated JSON event: {event_data['event_type']}")
    
    print("\nBasic tests completed!")
    print("Run 'python -m pytest tests/test_producer.py -v' for detailed tests") 