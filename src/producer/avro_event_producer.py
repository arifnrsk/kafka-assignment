#!/usr/bin/env python3
"""
Avro Kafka Event Producer
Kafka producer with Schema Registry integration for Avro serialization.
Produces structured Indonesian events with schema validation and evolution support.
"""

import time
import signal
import sys
import logging
from typing import Optional, Dict, Any
from confluent_kafka import Producer
from confluent_kafka.serialization import SerializationContext, MessageField

# Add src to path for imports
sys.path.append('src')

from utils.kafka_config import KafkaConfigManager
from utils.schema_registry import create_schema_registry_manager
from producer.avro_event_generator import create_avro_event_generator
from utils.logger import get_logger


class AvroKafkaEventProducer:
    """
    Kafka producer with Avro serialization support.
    
    Features:
    - Schema Registry integration
    - Avro binary serialization
    - Schema evolution support
    - Graceful shutdown handling
    - Comprehensive error handling
    - Production-ready logging
    """
    
    def __init__(self, config_file: str = None):
        """
        Initialize Avro Kafka Producer.
        
        Args:
            config_file: Optional path to configuration file
        """
        # Setup logging
        self.logger = get_logger('avro_producer')
        
        # Initialize components
        self.config_manager = KafkaConfigManager()
        self.schema_manager = create_schema_registry_manager()
        self.event_generator = create_avro_event_generator()
        
        # Producer state
        self.producer: Optional[Producer] = None
        self.running = False
        self.total_messages_sent = 0
        self.failed_messages = 0
        self.schema_id = None
        
        # Schema configuration
        self.topic_name = "random-events"
        self.schema_subject = f"{self.topic_name}-value"
        self.schema_file = "config/event_schema.avsc"
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info("Avro Kafka Producer initialized")
    
    def _signal_handler(self, signum: int, frame) -> None:
        """Handle shutdown signals gracefully."""
        self.logger.info(f"Received signal {signum}. Initiating graceful shutdown...")
        self.running = False
    
    def _create_producer(self) -> Producer:
        """
        Create and configure Confluent Kafka Producer.
        
        Returns:
            Configured Producer instance
            
        Raises:
            Exception: If producer creation fails
        """
        try:
            # Get basic Kafka configuration
            kafka_config = {
                'bootstrap.servers': 'localhost:9093',
                'client.id': 'avro-event-producer',
                'acks': 'all',
                'retries': 3,
                'batch.size': 16384,
                'linger.ms': 10,
                'compression.type': 'snappy',
                'max.in.flight.requests.per.connection': 1,
                'enable.idempotence': True
            }
            
            self.logger.info("Creating Confluent Kafka Producer with configuration:")
            for key, value in kafka_config.items():
                self.logger.info(f"  {key}: {value}")
            
            producer = Producer(kafka_config)
            
            self.logger.info("Confluent Kafka Producer created successfully")
            return producer
            
        except Exception as e:
            self.logger.error(f"Failed to create Kafka producer: {str(e)}")
            raise
    
    def _setup_schema(self) -> None:
        """
        Setup Avro schema with Schema Registry.
        
        Raises:
            Exception: If schema setup fails
        """
        try:
            self.logger.info("Setting up Avro schema...")
            
            # Health check Schema Registry
            if not self.schema_manager.health_check():
                raise Exception("Schema Registry is not accessible")
            
            # Load schema from file
            schema_str = self.schema_manager.load_schema_from_file(self.schema_file)
            self.logger.info(f"Loaded schema from {self.schema_file} ({len(schema_str)} chars)")
            
            # Register schema
            self.schema_id = self.schema_manager.register_schema(
                self.schema_subject, schema_str
            )
            self.logger.info(f"Schema registered with ID: {self.schema_id}")
            
            # Get serializer
            self.serializer = self.schema_manager.get_serializer(
                self.schema_subject, schema_str
            )
            self.logger.info("Avro serializer created successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to setup schema: {str(e)}")
            raise
    
    def _delivery_callback(self, err, msg) -> None:
        """
        Callback for message delivery confirmation.
        
        Args:
            err: Error object if delivery failed
            msg: Message object if delivery succeeded
        """
        if err is not None:
            self.failed_messages += 1
            self.logger.error(f"Message delivery failed: {err}")
        else:
            self.total_messages_sent += 1
            self.logger.debug(
                f"Message delivered to {msg.topic()} "
                f"[{msg.partition()}] at offset {msg.offset()}"
            )
    
    def _serialize_event(self, event_data: Dict[str, Any]) -> bytes:
        """
        Serialize event data using Avro schema.
        
        Args:
            event_data: Event data dictionary
            
        Returns:
            Serialized bytes
            
        Raises:
            Exception: If serialization fails
        """
        try:
            ctx = SerializationContext(self.schema_subject, MessageField.VALUE)
            serialized_data = self.serializer(event_data, ctx)
            
            self.logger.debug(f"Event serialized successfully ({len(serialized_data)} bytes)")
            return serialized_data
            
        except Exception as e:
            self.logger.error(f"Failed to serialize event: {str(e)}")
            raise
    
    def send_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Send single event to Kafka topic with Avro serialization.
        
        Args:
            event_data: Event data dictionary
            
        Returns:
            True if send initiated successfully, False otherwise
        """
        try:
            # Serialize event data
            serialized_data = self._serialize_event(event_data)
            
            # Use session_id as key for partitioning
            key = event_data.get('session_id', '')
            
            # Send message
            self.producer.produce(
                topic=self.topic_name,
                key=key,
                value=serialized_data,
                callback=self._delivery_callback
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send event: {str(e)}")
            self.failed_messages += 1
            return False
    
    def start_producing(self) -> None:
        """Start producing Avro events every 5 seconds."""
        try:
            self.logger.info("Starting Avro Event Producer...")
            
            # Create producer
            self.producer = self._create_producer()
            
            # Setup schema
            self._setup_schema()
            
            # Production configuration
            interval = 5  # seconds
            
            self.logger.info(f"Starting event production to topic '{self.topic_name}'")
            self.logger.info(f"Schema subject: {self.schema_subject}")
            self.logger.info(f"Schema ID: {self.schema_id}")
            self.logger.info(f"Event generation interval: {interval} seconds")
            self.logger.info("Press Ctrl+C to stop...")
            
            self.running = True
            
            while self.running:
                try:
                    # Generate Avro-compatible event
                    event_data = self.event_generator.generate_avro_event()
                    
                    # Send event
                    success = self.send_event(event_data)
                    
                    if success:
                        self.logger.info(
                            f"Sent event: {event_data['event_type']} "
                            f"(ID: {event_data['event_id'][:8]}...) "
                            f"from {event_data['location']['city']}"
                        )
                        
                        # Log additional details
                        if event_data['event_data']['value']:
                            self.logger.info(
                                f"   Value: {event_data['event_data']['value']} "
                                f"{event_data['event_data']['currency']}"
                            )
                        
                        self.logger.info(
                            f"   Device: {event_data['device_info']['device_type']}"
                        )
                        self.logger.info(
                            f"   Status: {event_data['event_data']['status']}"
                        )
                    
                    # Poll for delivery callbacks
                    self.producer.poll(0)
                    
                    # Wait for next event
                    time.sleep(interval)
                    
                except KeyboardInterrupt:
                    self.logger.info("Keyboard interrupt received")
                    break
                except Exception as e:
                    self.logger.error(f"Error in production loop: {str(e)}")
                    time.sleep(1)  # Brief pause before retry
            
        except Exception as e:
            self.logger.error(f"Fatal error in producer: {str(e)}")
        finally:
            self._cleanup()
    
    def _cleanup(self) -> None:
        """Cleanup resources and print statistics."""
        self.logger.info("Cleaning up resources...")
        
        if self.producer:
            try:
                # Flush any remaining messages
                self.logger.info("Flushing remaining messages...")
                self.producer.flush(timeout=30)
                
                self.logger.info("Producer closed successfully")
            except Exception as e:
                self.logger.error(f"Error during cleanup: {str(e)}")
        
        # Print final statistics
        self._print_statistics()
    
    def _print_statistics(self) -> None:
        """Print production statistics."""
        total_attempts = self.total_messages_sent + self.failed_messages
        
        self.logger.info("=" * 50)
        self.logger.info("PRODUCTION STATISTICS")
        self.logger.info("=" * 50)
        self.logger.info(f"Total messages sent: {self.total_messages_sent}")
        self.logger.info(f"Failed messages: {self.failed_messages}")
        self.logger.info(f"Total attempts: {total_attempts}")
        
        if total_attempts > 0:
            success_rate = (self.total_messages_sent / total_attempts) * 100
            self.logger.info(f"Success rate: {success_rate:.2f}%")
        
        if self.schema_id:
            self.logger.info(f"Schema ID used: {self.schema_id}")
        
        self.logger.info("=" * 50)


def main():
    """Main function to start the Avro producer."""
    print("Starting Avro Kafka Event Producer...")
    print("=" * 50)
    print("Features:")
    print("- Schema Registry integration")
    print("- Avro binary serialization")
    print("- Schema evolution support")
    print("- Comprehensive error handling")
    print("=" * 50)
    
    try:
        producer = AvroKafkaEventProducer()
        producer.start_producing()
    except Exception as e:
        logging.error(f"Failed to start producer: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 