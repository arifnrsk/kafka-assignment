"""
Unit tests for Kafka Consumer components
"""
import pytest
import json
import sys
import os
from datetime import datetime, timezone

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from consumer.processor import EventProcessor, ProcessingResult
from consumer.event_consumer import KafkaEventConsumer
from producer.event_generator import EventGenerator


class TestEventProcessor:
    """Test cases for EventProcessor"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.processor = EventProcessor()
        self.generator = EventGenerator()
    
    def test_processor_initialization(self):
        """Test processor initialization"""
        assert self.processor.logger is not None
        assert isinstance(self.processor.processed_events, list)
        assert len(self.processor.processed_events) == 0
        assert self.processor.processing_stats['total_processed'] == 0
        assert self.processor.processing_stats['processing_errors'] == 0
    
    def test_process_valid_event(self):
        """Test processing a valid event"""
        # Generate a test event
        event_json = self.generator.generate_event_json()
        
        # Process the event
        result = self.processor.process_event(event_json)
        
        # Check result
        assert result is not None
        assert isinstance(result, ProcessingResult)
        assert result.event_id is not None
        assert result.processed_at is not None
        assert isinstance(result.calculations, dict)
        assert isinstance(result.summary, str)
        assert isinstance(result.alerts, list)
        
        # Check statistics were updated
        assert self.processor.processing_stats['total_processed'] == 1
        assert len(self.processor.processed_events) == 1
    
    def test_process_invalid_json(self):
        """Test processing invalid JSON"""
        invalid_json = "{ invalid json }"
        
        result = self.processor.process_event(invalid_json)
        
        # Should return None for invalid JSON
        assert result is None
        assert self.processor.processing_stats['processing_errors'] == 1
    
    def test_calculations(self):
        """Test event calculations"""
        # Create a test event with known values
        test_event = {
            "event_id": "test-123",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "purchase",
            "user_id": 1234,
            "value": 750.0,
            "status": "success",
            "location": {"city": "Jakarta", "country": "Indonesia"},
            "metadata": {"category": "electronics"}
        }
        
        event_json = json.dumps(test_event)
        result = self.processor.process_event(event_json)
        
        assert result is not None
        calc = result.calculations
        
        # Test value categorization
        assert calc.get('value_category') == 'very_high'  # 750 > 500
        
        # Test risk score calculation
        assert 'risk_score' in calc
        assert isinstance(calc['risk_score'], float)
        assert calc['risk_score'] >= 0.0 and calc['risk_score'] <= 1.0
        
        # Test event age calculation
        assert 'event_age_seconds' in calc
        assert isinstance(calc['event_age_seconds'], (int, float))
    
    def test_risk_score_calculation(self):
        """Test risk score calculation with different scenarios"""
        # High value event
        high_value_event = {
            "event_id": "test-high-value",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "purchase",
            "value": 900.0,  # High value
            "status": "success"
        }
        
        result = self.processor.process_event(json.dumps(high_value_event))
        assert result.calculations['risk_score'] >= 0.3
        
        # Failed event
        failed_event = {
            "event_id": "test-failed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "purchase",
            "value": 100.0,
            "status": "failed"  # Failed status
        }
        
        result = self.processor.process_event(json.dumps(failed_event))
        assert result.calculations['risk_score'] >= 0.4
        
        # Error event
        error_event = {
            "event_id": "test-error",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "error",  # Error type
            "value": 50.0,
            "status": "success"
        }
        
        result = self.processor.process_event(json.dumps(error_event))
        assert result.calculations['risk_score'] >= 0.5
    
    def test_alert_generation(self):
        """Test alert generation"""
        # High value event that should trigger alerts
        high_risk_event = {
            "event_id": "test-alerts",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "error",
            "value": 900.0,  # High value
            "status": "failed",  # Failed status
            "user_id": 1234
        }
        
        result = self.processor.process_event(json.dumps(high_risk_event))
        
        # Should have multiple alerts
        assert len(result.alerts) > 0
        
        # Check for specific alert types
        alert_text = ' '.join(result.alerts)
        assert 'High value transaction' in alert_text or 'Error event' in alert_text
    
    def test_statistics_tracking(self):
        """Test statistics tracking across multiple events"""
        # Process multiple events
        events_data = []
        for i in range(5):
            event_json = self.generator.generate_event_json()
            events_data.append(json.loads(event_json))
            self.processor.process_event(event_json)
        
        # Check statistics
        stats = self.processor.processing_stats
        assert stats['total_processed'] == 5
        assert len(stats['event_types']) > 0
        assert len(stats['total_values']) == 5
        
        # Test summary generation
        summary = self.processor.get_processing_summary()
        assert 'value_statistics' in summary
        assert 'top_event_types' in summary
        assert summary['value_statistics']['count'] == 5
    
    def test_user_activity_tracking(self):
        """Test user activity tracking"""
        user_id = 1234
        
        # Create multiple events for same user
        for i in range(3):
            event = {
                "event_id": f"test-user-{i}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event_type": "page_view",
                "user_id": user_id,
                "value": 50.0,
                "status": "success"
            }
            self.processor.process_event(json.dumps(event))
        
        # Check user activity tracking
        assert self.processor.processing_stats['user_activities'][user_id] == 3
        
        # Process another event for same user
        event = {
            "event_id": "test-user-4",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "purchase",
            "user_id": user_id,
            "value": 100.0,
            "status": "success"
        }
        
        result = self.processor.process_event(json.dumps(event))
        assert result.calculations['user_activity_count'] == 4
        assert result.calculations['user_activity_level'] == 'medium'


class TestKafkaEventConsumer:
    """Test cases for KafkaEventConsumer"""
    
    def setup_method(self):
        """Setup test fixtures"""
        # Note: These tests don't actually connect to Kafka
        pass
    
    def test_consumer_initialization(self):
        """Test consumer initialization"""
        consumer = KafkaEventConsumer()
        
        assert consumer.config_manager is not None
        assert consumer.logger is not None
        assert consumer.processor is not None
        assert consumer.consumer is None  # Not connected yet
        assert consumer.running is False
        assert consumer.total_messages_consumed == 0
        assert consumer.processing_errors == 0
    
    def test_signal_handler(self):
        """Test signal handler setup"""
        consumer = KafkaEventConsumer()
        
        # Simulate signal
        consumer._signal_handler(2, None)  # SIGINT
        assert consumer.running is False


if __name__ == "__main__":
    # Run basic tests
    print("Running Consumer Tests...")
    
    # Test EventProcessor
    print("\nTesting EventProcessor...")
    processor = EventProcessor()
    generator = EventGenerator()
    
    # Process a few events
    for i in range(3):
        event_json = generator.generate_event_json()
        result = processor.process_event(event_json)
        if result:
            print(f"   Event {i+1}: {result.summary[:50]}...")
            if result.alerts:
                print(f"      Alerts: {len(result.alerts)}")
    
    # Print statistics
    print("\nProcessing Statistics:")
    stats = processor.get_processing_summary()
    print(f"   Total processed: {stats['total_processed']}")
    print(f"   Event types: {list(stats['top_event_types'].keys())[:3]}")
    
    if stats.get('value_statistics'):
        val_stats = stats['value_statistics']
        print(f"   Value range: ${val_stats['min']} - ${val_stats['max']}")
    
    print("\nBasic tests completed!")
    print("Run 'python -m pytest tests/test_consumer.py -v' for detailed tests") 