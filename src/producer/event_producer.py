#!/usr/bin/env python3
"""
Kafka Event Producer
Produces random events every 5 seconds to Kafka topic
"""
import time
import json
import signal
import sys
from typing import Optional
from kafka import KafkaProducer
from kafka.errors import KafkaError

# Add src to path for imports
sys.path.append('src')

from utils import kafka_config_manager, producer_logger
from producer.event_generator import EventGenerator


class KafkaEventProducer:
    """Kafka producer for generating random events"""
    
    def __init__(self):
        self.config_manager = kafka_config_manager
        self.logger = producer_logger
        self.event_generator = EventGenerator()
        self.producer: Optional[KafkaProducer] = None
        self.running = False
        self.total_messages_sent = 0
        self.failed_messages = 0
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}. Shutting down gracefully...")
        self.running = False
    
    def _create_producer(self) -> KafkaProducer:
        """Create and configure Kafka producer"""
        try:
            producer_config = self.config_manager.get_producer_config()
            
            self.logger.info("Creating Kafka producer with configuration:")
            self.logger.info(f"Bootstrap servers: {producer_config['bootstrap_servers']}")
            self.logger.info(f"Acks: {producer_config['acks']}")
            self.logger.info(f"Batch size: {producer_config['batch_size']}")
            
            producer = KafkaProducer(**producer_config)
            
            self.logger.info("Kafka producer created successfully")
            return producer
            
        except Exception as e:
            self.logger.error(f"Failed to create Kafka producer: {str(e)}")
            raise
    
    def _delivery_callback(self, record_metadata=None, exception=None):
        """Callback for message delivery confirmation"""
        if exception is not None:
            self.failed_messages += 1
            self.logger.error(f"Message delivery failed: {str(exception)}")
        else:
            self.total_messages_sent += 1
            self.logger.debug(
                f"Message delivered to {record_metadata.topic} "
                f"[{record_metadata.partition}] at offset {record_metadata.offset}"
            )
    
    def send_event(self, event_data: str, key: Optional[str] = None) -> bool:
        """Send single event to Kafka topic"""
        try:
            topic_config = self.config_manager.get_topic_config()
            topic_name = topic_config['topic']
            
            # Send message asynchronously
            future = self.producer.send(
                topic=topic_name,
                value=event_data,
                key=key
            )
            
            # Add callback for delivery confirmation
            future.add_callback(self._delivery_callback)
            future.add_errback(lambda ex: self._delivery_callback(exception=ex))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send event: {str(e)}")
            self.failed_messages += 1
            return False
    
    def start_producing(self):
        """Start producing events every 5 seconds"""
        try:
            # Validate configuration
            if not self.config_manager.validate_config():
                self.logger.error("Invalid configuration. Exiting...")
                return
            
            # Create producer
            self.producer = self._create_producer()
            
            # Get event generation interval
            interval = self.config_manager.config.event_generation_interval
            topic_name = self.config_manager.config.topic_name
            
            self.logger.info(f"Starting event production to topic '{topic_name}'")
            self.logger.info(f"Event generation interval: {interval} seconds")
            self.logger.info("Press Ctrl+C to stop...")
            
            self.running = True
            
            while self.running:
                try:
                    # Generate random event
                    event_json = self.event_generator.generate_event_json()
                    event_data = json.loads(event_json)
                    
                    # Use user_id as key for partitioning
                    key = str(event_data.get('user_id', ''))
                    
                    # Send event
                    success = self.send_event(event_json, key)
                    
                    if success:
                        self.logger.info(
                            f"Sent event: {event_data['event_type']} "
                            f"(ID: {event_data['event_id'][:8]}...) "
                            f"for user {event_data['user_id']}"
                        )
                        
                        # Log some event details
                        self.logger.info(
                            f"   Location: {event_data['location']['city']}"
                        )
                        self.logger.info(
                            f"   Value: ${event_data['value']}"
                        )
                        self.logger.info(
                            f"   Device: {event_data['device_type']}"
                        )
                    
                    # Flush producer to ensure delivery
                    self.producer.flush(timeout=10)
                    
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
    
    def _cleanup(self):
        """Cleanup resources"""
        self.logger.info("Cleaning up resources...")
        
        if self.producer:
            try:
                # Flush any remaining messages
                self.producer.flush(timeout=30)
                # Close producer
                self.producer.close(timeout=30)
                self.logger.info("Producer closed successfully")
            except Exception as e:
                self.logger.error(f"Error closing producer: {str(e)}")
        
        # Print statistics
        self.logger.info("Production Statistics:")
        self.logger.info(f"   Total messages sent: {self.total_messages_sent}")
        self.logger.info(f"   Failed messages: {self.failed_messages}")
        
        if self.total_messages_sent > 0:
            success_rate = (self.total_messages_sent / 
                          (self.total_messages_sent + self.failed_messages)) * 100
            self.logger.info(f"   Success rate: {success_rate:.2f}%")


def main():
    """Main function to start the producer"""
    print("Starting Kafka Event Producer...")
    print("=" * 50)
    
    producer = KafkaEventProducer()
    producer.start_producing()


if __name__ == "__main__":
    main() 