#!/usr/bin/env python3
"""
Kafka Event Consumer
Consumes events from Kafka topic and processes them
"""
import signal
import sys
import json
from typing import Optional
from kafka import KafkaConsumer
from kafka.errors import KafkaError

# Add src to path for imports
sys.path.append('src')

from utils import kafka_config_manager, consumer_logger
from consumer.processor import EventProcessor


class KafkaEventConsumer:
    """Kafka consumer for processing events"""
    
    def __init__(self):
        self.config_manager = kafka_config_manager
        self.logger = consumer_logger
        self.processor = EventProcessor()
        self.consumer: Optional[KafkaConsumer] = None
        self.running = False
        self.total_messages_consumed = 0
        self.processing_errors = 0
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}. Shutting down gracefully...")
        self.running = False
    
    def _create_consumer(self) -> KafkaConsumer:
        """Create and configure Kafka consumer"""
        try:
            consumer_config = self.config_manager.get_consumer_config()
            topic_config = self.config_manager.get_topic_config()
            topic_name = topic_config['topic']
            
            self.logger.info("Creating Kafka consumer with configuration:")
            self.logger.info(f"Bootstrap servers: {consumer_config['bootstrap_servers']}")
            self.logger.info(f"Group ID: {consumer_config['group_id']}")
            self.logger.info(f"Auto offset reset: {consumer_config['auto_offset_reset']}")
            self.logger.info(f"Topic: {topic_name}")
            
            # Create consumer and subscribe to topic
            consumer = KafkaConsumer(
                topic_name,
                **consumer_config
            )
            
            self.logger.info("Kafka consumer created successfully")
            self.logger.info(f"Subscribed to topic: {topic_name}")
            
            return consumer
            
        except Exception as e:
            self.logger.error(f"Failed to create Kafka consumer: {str(e)}")
            raise
    
    def start_consuming(self):
        """Start consuming events from Kafka topic"""
        try:
            # Validate configuration
            if not self.config_manager.validate_config():
                self.logger.error("Invalid configuration. Exiting...")
                return
            
            # Create consumer
            self.consumer = self._create_consumer()
            
            topic_name = self.config_manager.config.topic_name
            consumer_group = self.config_manager.config.consumer_group_id
            
            self.logger.info(f"Starting event consumption from topic '{topic_name}'")
            self.logger.info(f"Consumer group: {consumer_group}")
            self.logger.info("Press Ctrl+C to stop...")
            
            self.running = True
            
            # Start consuming messages with timeout for graceful shutdown
            while self.running:
                try:
                    # Poll for messages with timeout (1 second)
                    message_batch = self.consumer.poll(timeout_ms=1000)
                    
                    if not message_batch:
                        # No messages received, continue to check running flag
                        continue
                    
                    # Process all messages in the batch
                    for topic_partition, messages in message_batch.items():
                        for message in messages:
                            if not self.running:
                                break
                            
                            try:
                                # Process the message
                                self._process_message(message)
                                
                                # Log progress every 10 messages
                                if self.total_messages_consumed % 10 == 0 and self.total_messages_consumed > 0:
                                    self._log_progress()
                                
                            except Exception as e:
                                self.logger.error(f"Error processing message: {str(e)}")
                                self.processing_errors += 1
                        
                        if not self.running:
                            break
                    
                except Exception as e:
                    self.logger.error(f"Error polling messages: {str(e)}")
                    if not self.running:
                        break
            
        except Exception as e:
            self.logger.error(f"Fatal error in consumer: {str(e)}")
        finally:
            self._cleanup()
    
    def _process_message(self, message):
        """Process a single Kafka message"""
        try:
            # Extract message data
            topic = message.topic
            partition = message.partition
            offset = message.offset
            key = message.key if message.key else None
            value = message.value
            timestamp = message.timestamp
            
            self.total_messages_consumed += 1
            
            self.logger.info(f"Received message from {topic}[{partition}] at offset {offset}")
            
            if key:
                self.logger.info(f"Message key: {key}")
            
            # Parse the event data
            try:
                event_data = json.loads(value)
                self.logger.info(f"Event type: {event_data.get('event_type', 'unknown')}")
                self.logger.info(f"User ID: {event_data.get('user_id', 'unknown')}")
                
                # Log event details
                if event_data.get('location'):
                    location = event_data['location']
                    self.logger.info(f"Location: {location.get('city', 'unknown')}")
                
                self.logger.info(f"Value: ${event_data.get('value', 0)}")
                self.logger.info(f"Device: {event_data.get('device_type', 'unknown')}")
                
            except json.JSONDecodeError:
                self.logger.warning("Message is not valid JSON, processing as plain text")
                event_data = {'raw_message': value}
            
            # Process the event using our processor
            result = self.processor.process_event(value)
            
            if result:
                self.logger.info(f"Processing result: {result.summary}")
                
                # Log calculations
                if result.calculations:
                    calc = result.calculations
                    self.logger.info(f"Calculations:")
                    
                    if calc.get('risk_score'):
                        risk_level = "HIGH" if calc['risk_score'] > 0.5 else "MEDIUM" if calc['risk_score'] > 0.2 else "LOW"
                        self.logger.info(f"   Risk Score: {calc['risk_score']:.2f} ({risk_level})")
                    
                    if calc.get('value_category'):
                        self.logger.info(f"   Value Category: {calc['value_category']}")
                    
                    if calc.get('user_activity_level'):
                        self.logger.info(f"   User Activity: {calc['user_activity_level']}")
                    
                    if calc.get('event_age_seconds'):
                        self.logger.info(f"   Event Age: {calc['event_age_seconds']} seconds")
                
                # Log alerts if any
                if result.alerts:
                    for alert in result.alerts:
                        self.logger.warning(f"ALERT: {alert}")
            
            else:
                self.logger.error("Failed to process event")
                self.processing_errors += 1
            
            self.logger.info("-" * 60)
            
        except Exception as e:
            self.logger.error(f"Error in message processing: {str(e)}")
            self.processing_errors += 1
    
    def _log_progress(self):
        """Log consumption progress"""
        self.logger.info("CONSUMPTION PROGRESS:")
        self.logger.info(f"   Total messages consumed: {self.total_messages_consumed}")
        self.logger.info(f"   Processing errors: {self.processing_errors}")
        
        if self.total_messages_consumed > 0:
            success_rate = ((self.total_messages_consumed - self.processing_errors) / 
                          self.total_messages_consumed) * 100
            self.logger.info(f"   Success rate: {success_rate:.2f}%")
        
        # Get processing statistics
        proc_stats = self.processor.get_processing_summary()
        self.logger.info(f"   Events processed: {proc_stats['total_processed']}")
        
        if proc_stats.get('top_event_types'):
            self.logger.info(f"   Top event types: {dict(list(proc_stats['top_event_types'].items())[:3])}")
        
        if proc_stats.get('value_statistics'):
            val_stats = proc_stats['value_statistics']
            self.logger.info(f"   Value stats - Avg: ${val_stats['mean']}, Max: ${val_stats['max']}")
        
        self.logger.info("=" * 60)
    
    def _cleanup(self):
        """Cleanup resources"""
        self.logger.info("Cleaning up resources...")
        
        if self.consumer:
            try:
                # Commit any pending offsets
                self.consumer.commit()
                self.logger.info("Offsets committed successfully")
                
                # Close consumer with timeout
                self.consumer.close()
                self.logger.info("Consumer closed successfully")
            except Exception as e:
                self.logger.error(f"Error closing consumer: {str(e)}")
        
        # Print final statistics
        self.logger.info("FINAL CONSUMPTION STATISTICS:")
        self.logger.info(f"   Total messages consumed: {self.total_messages_consumed}")
        self.logger.info(f"   Processing errors: {self.processing_errors}")
        
        if self.total_messages_consumed > 0:
            success_rate = ((self.total_messages_consumed - self.processing_errors) / 
                          self.total_messages_consumed) * 100
            self.logger.info(f"   Overall success rate: {success_rate:.2f}%")
        
        # Print processing summary
        proc_summary = self.processor.get_processing_summary()
        self.logger.info("PROCESSING SUMMARY:")
        self.logger.info(f"   Total events processed: {proc_summary['total_processed']}")
        
        if proc_summary.get('top_event_types'):
            self.logger.info(f"   Event types: {proc_summary['top_event_types']}")
        
        if proc_summary.get('top_locations'):
            self.logger.info(f"   Top locations: {proc_summary['top_locations']}")
        
        if proc_summary.get('value_statistics'):
            val_stats = proc_summary['value_statistics']
            self.logger.info(f"   Value statistics:")
            self.logger.info(f"      Mean: ${val_stats['mean']}")
            self.logger.info(f"      Median: ${val_stats['median']}")
            self.logger.info(f"      Range: ${val_stats['min']} - ${val_stats['max']}")


def main():
    """Main function to start the consumer"""
    print("Starting Kafka Event Consumer...")
    print("=" * 50)
    
    consumer = KafkaEventConsumer()
    consumer.start_consuming()


if __name__ == "__main__":
    main() 