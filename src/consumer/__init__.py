"""
Consumer package for Kafka assignment
Contains event consumption and processing logic
"""

from .processor import EventProcessor, ProcessingResult
from .event_consumer import KafkaEventConsumer

__all__ = [
    'EventProcessor',
    'ProcessingResult',
    'KafkaEventConsumer'
] 