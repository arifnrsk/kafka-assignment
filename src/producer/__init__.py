"""
Producer package for Kafka assignment
Contains event generation and producer logic
"""

from .event_generator import EventGenerator, EventData, create_random_event
from .event_producer import KafkaEventProducer

__all__ = [
    'EventGenerator',
    'EventData', 
    'create_random_event',
    'KafkaEventProducer'
] 