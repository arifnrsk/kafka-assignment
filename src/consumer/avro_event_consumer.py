#!/usr/bin/env python3
"""
Avro Kafka Event Consumer
Kafka consumer with Schema Registry integration for Avro deserialization.
Processes structured Indonesian events with schema validation and analytics.
"""

import signal
import sys
import logging
from typing import Optional, Dict, Any
from confluent_kafka import Consumer, KafkaError
from confluent_kafka.serialization import SerializationContext, MessageField

# Add src to path for imports
sys.path.append('src')

from utils.kafka_config import KafkaConfigManager
from utils.schema_registry import create_schema_registry_manager
from consumer.processor import EventProcessor
from utils.logger import get_logger


class AvroKafkaEventConsumer:
    """
    Kafka consumer with Avro deserialization support.
    
    Features:
    - Schema Registry integration
    - Avro binary deserialization
    - Schema evolution support
    - Advanced event processing
    - Graceful shutdown handling
    - Comprehensive analytics
    """
    
    def __init__(self, config_file: str = None):
        """
        Initialize Avro Kafka Consumer.
        
        Args:
            config_file: Optional path to configuration file
        """
        # Setup logging
        self.logger = get_logger('avro_consumer')
        
        # Initialize components
        self.config_manager = KafkaConfigManager()
        self.schema_manager = create_schema_registry_manager()
        self.processor = EventProcessor()
        
        # Consumer state
        self.consumer: Optional[Consumer] = None
        self.running = False
        self.total_messages_consumed = 0
        self.processing_errors = 0
        self.deserializer = None
        
        # Configuration
        self.topic_name = "random-events"
        self.schema_subject = f"{self.topic_name}-value"
        self.consumer_group = "avro-event-processors"
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info("Avro Kafka Consumer initialized")
    
    def _signal_handler(self, signum: int, frame) -> None:
        """Handle shutdown signals gracefully."""
        self.logger.info(f"Received signal {signum}. Initiating graceful shutdown...")
        self.running = False
    
    def _create_consumer(self) -> Consumer:
        """
        Create and configure Confluent Kafka Consumer.
        
        Returns:
            Configured Consumer instance
            
        Raises:
            Exception: If consumer creation fails
        """
        try:
            # Consumer configuration
            consumer_config = {
                'bootstrap.servers': 'localhost:9093',
                'group.id': self.consumer_group,
                'client.id': 'avro-event-consumer',
                'auto.offset.reset': 'earliest',
                'enable.auto.commit': True,
                'auto.commit.interval.ms': 5000,
                'max.poll.interval.ms': 300000,
                'session.timeout.ms': 30000,
                'heartbeat.interval.ms': 10000,
                'fetch.min.bytes': 1
            }
            
            self.logger.info("Creating Confluent Kafka Consumer with configuration:")
            for key, value in consumer_config.items():
                self.logger.info(f"  {key}: {value}")
            
            consumer = Consumer(consumer_config)
            
            self.logger.info("Confluent Kafka Consumer created successfully")
            return consumer
            
        except Exception as e:
            self.logger.error(f"Failed to create Kafka consumer: {str(e)}")
            raise
    
    def _setup_schema(self) -> None:
        """
        Setup Avro schema with Schema Registry.
        
        Raises:
            Exception: If schema setup fails
        """
        try:
            self.logger.info("Setting up Avro schema for deserialization...")
            
            # Health check Schema Registry
            if not self.schema_manager.health_check():
                raise Exception("Schema Registry is not accessible")
            
            # Get schema from registry
            schema_str = self.schema_manager.get_schema(self.schema_subject)
            if not schema_str:
                raise Exception(f"Schema not found for subject: {self.schema_subject}")
            
            self.logger.info(f"Retrieved schema for subject: {self.schema_subject}")
            
            # Get deserializer
            self.deserializer = self.schema_manager.get_deserializer(
                self.schema_subject, schema_str
            )
            self.logger.info("Avro deserializer created successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to setup schema: {str(e)}")
            raise
    
    def _deserialize_message(self, message_value: bytes) -> Dict[str, Any]:
        """
        Deserialize Avro message.
        
        Args:
            message_value: Serialized message bytes
            
        Returns:
            Deserialized event data dictionary
            
        Raises:
            Exception: If deserialization fails
        """
        try:
            ctx = SerializationContext(self.schema_subject, MessageField.VALUE)
            event_data = self.deserializer(message_value, ctx)
            
            self.logger.debug(f"Message deserialized successfully")
            return event_data
            
        except Exception as e:
            self.logger.error(f"Failed to deserialize message: {str(e)}")
            raise
    
    def _process_message(self, message) -> None:
        """
        Process a single Kafka message.
        
        Args:
            message: Kafka message object
        """
        try:
            # Extract message metadata
            topic = message.topic()
            partition = message.partition()
            offset = message.offset()
            key = message.key().decode('utf-8') if message.key() else None
            timestamp = message.timestamp()
            
            # Deserialize Avro message
            event_data = self._deserialize_message(message.value())
            
            # Log message reception
            self.logger.info(
                f"Received Avro event: {event_data['event_type']} "
                f"(ID: {event_data['event_id'][:8]}...) "
                f"from {event_data['location']['city']}"
            )
            
            # Log message metadata
            self.logger.debug(f"Message metadata:")
            self.logger.debug(f"  Topic: {topic}")
            self.logger.debug(f"  Partition: {partition}")
            self.logger.debug(f"  Offset: {offset}")
            self.logger.debug(f"  Key: {key}")
            self.logger.debug(f"  Timestamp: {timestamp}")
            
            # Process event with analytics
            self.processor.process_event(event_data)
            
            # Increment counter
            self.total_messages_consumed += 1
            
            # Log event details
            self._log_event_details(event_data)
            
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            self.processing_errors += 1
    
    def _log_event_details(self, event_data: Dict[str, Any]) -> None:
        """
        Log detailed event information.
        
        Args:
            event_data: Deserialized event data
        """
        try:
            # Basic event info
            self.logger.info(f"Event Details:")
            self.logger.info(f"  Type: {event_data['event_type']}")
            self.logger.info(f"  User ID: {event_data.get('user_id', 'Anonymous')}")
            self.logger.info(f"  Session: {event_data['session_id']}")
            
            # Location info
            location = event_data['location']
            self.logger.info(f"  Location: {location['city']}, {location.get('province', 'N/A')}")
            
            # Device info
            device = event_data['device_info']
            self.logger.info(f"  Device: {device['device_type']}")
            if device.get('os'):
                self.logger.info(f"  OS: {device['os']}")
            
            # Event data
            event_details = event_data['event_data']
            self.logger.info(f"  Status: {event_details['status']}")
            
            if event_details.get('value'):
                self.logger.info(
                    f"  Value: {event_details['value']} {event_details['currency']}"
                )
            
            if event_details.get('category'):
                self.logger.info(f"  Category: {event_details['category']}")
            
            # Metadata
            metadata = event_data['metadata']
            self.logger.info(f"  Source: {metadata['source']}")
            self.logger.info(f"  Environment: {metadata['environment']}")
            
        except Exception as e:
            self.logger.warning(f"Failed to log event details: {str(e)}")
    
    def _log_progress(self) -> None:
        """Log consumption progress and statistics."""
        total_processed = self.total_messages_consumed + self.processing_errors
        
        if total_processed > 0:
            success_rate = (self.total_messages_consumed / total_processed) * 100
            
            self.logger.info("=" * 40)
            self.logger.info("CONSUMPTION PROGRESS")
            self.logger.info("=" * 40)
            self.logger.info(f"Messages consumed: {self.total_messages_consumed}")
            self.logger.info(f"Processing errors: {self.processing_errors}")
            self.logger.info(f"Success rate: {success_rate:.2f}%")
            
            # Get processor statistics
            processor_stats = self.processor.get_processing_summary()
            self.logger.info(f"Risk alerts: {processor_stats.get('high_risk_events', 0)}")
            self.logger.info(f"Total value processed: {len(processor_stats.get('total_values', []))}")
            self.logger.info("=" * 40)
    
    def start_consuming(self) -> None:
        """Start consuming Avro events from Kafka."""
        try:
            self.logger.info("Starting Avro Event Consumer...")
            
            # Create consumer
            self.consumer = self._create_consumer()
            
            # Setup schema
            self._setup_schema()
            
            # Subscribe to topic
            self.consumer.subscribe([self.topic_name])
            self.logger.info(f"Subscribed to topic: {self.topic_name}")
            self.logger.info(f"Consumer group: {self.consumer_group}")
            self.logger.info("Waiting for messages... Press Ctrl+C to stop")
            
            self.running = True
            
            while self.running:
                try:
                    # Poll for messages with timeout
                    message = self.consumer.poll(timeout=1.0)
                    
                    if message is None:
                        continue
                    
                    if message.error():
                        if message.error().code() == KafkaError._PARTITION_EOF:
                            self.logger.debug(
                                f"End of partition reached {message.topic()} "
                                f"[{message.partition()}] at offset {message.offset()}"
                            )
                        else:
                            self.logger.error(f"Consumer error: {message.error()}")
                        continue
                    
                    # Process the message
                    self._process_message(message)
                    
                    # Log progress every 10 messages
                    if self.total_messages_consumed % 10 == 0 and self.total_messages_consumed > 0:
                        self._log_progress()
                    
                except KeyboardInterrupt:
                    self.logger.info("Keyboard interrupt received")
                    break
                except Exception as e:
                    self.logger.error(f"Error in consumption loop: {str(e)}")
                    self.processing_errors += 1
            
        except Exception as e:
            self.logger.error(f"Fatal error in consumer: {str(e)}")
        finally:
            self._cleanup()
    
    def _cleanup(self) -> None:
        """Cleanup resources and print final statistics."""
        self.logger.info("Cleaning up resources...")
        
        if self.consumer:
            try:
                # Commit any pending offsets
                self.consumer.commit()
                self.logger.info("Offsets committed successfully")
                
                # Close consumer
                self.consumer.close()
                self.logger.info("Consumer closed successfully")
                
            except Exception as e:
                self.logger.error(f"Error during cleanup: {str(e)}")
        
        # Print final statistics
        self._print_final_statistics()
    
    def _print_final_statistics(self) -> None:
        """Print final consumption statistics."""
        total_processed = self.total_messages_consumed + self.processing_errors
        
        self.logger.info("=" * 60)
        self.logger.info("FINAL CONSUMPTION STATISTICS")
        self.logger.info("=" * 60)
        self.logger.info(f"Total messages consumed: {self.total_messages_consumed}")
        self.logger.info(f"Processing errors: {self.processing_errors}")
        self.logger.info(f"Total processed: {total_processed}")
        
        if total_processed > 0:
            success_rate = (self.total_messages_consumed / total_processed) * 100
            self.logger.info(f"Success rate: {success_rate:.2f}%")
        
        # Get final processor statistics
        try:
            processor_stats = self.processor.get_processing_summary()
            self.logger.info("Event Processing Analytics:")
            for key, value in processor_stats.items():
                if isinstance(value, dict):
                    self.logger.info(f"  {key}:")
                    for sub_key, sub_value in value.items():
                        self.logger.info(f"    {sub_key}: {sub_value}")
                else:
                    self.logger.info(f"  {key}: {value}")
        except Exception as e:
            self.logger.warning(f"Failed to get processor statistics: {str(e)}")
        
        self.logger.info("=" * 60)


def main():
    """Main function to start the Avro consumer."""
    print("Starting Avro Kafka Event Consumer...")
    print("=" * 50)
    print("Features:")
    print("- Schema Registry integration")
    print("- Avro binary deserialization")
    print("- Schema evolution support")
    print("- Advanced event analytics")
    print("- Comprehensive error handling")
    print("=" * 50)
    
    try:
        consumer = AvroKafkaEventConsumer()
        consumer.start_consuming()
    except Exception as e:
        logging.error(f"Failed to start consumer: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 