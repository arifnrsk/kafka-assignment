"""
Kafka Configuration Module
Handles all Kafka connection settings and topic configurations
"""
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from decouple import config


@dataclass
class KafkaConfig:
    """Kafka configuration data class"""
    bootstrap_servers: str
    topic_name: str
    partitions: int
    replication_factor: int
    consumer_group_id: str
    
    # Producer settings
    producer_acks: str
    producer_batch_size: int
    producer_linger_ms: int
    
    # Consumer settings
    consumer_auto_offset_reset: str
    consumer_enable_auto_commit: bool
    consumer_auto_commit_interval_ms: int
    
    # Application settings
    event_generation_interval: int
    log_level: str


class KafkaConfigManager:
    """Manages Kafka configuration with environment variable support"""
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> KafkaConfig:
        """Load configuration from environment variables"""
        return KafkaConfig(
            # Connection settings
            bootstrap_servers=config(
                'KAFKA_BOOTSTRAP_SERVERS', 
                default='localhost:9093'
            ),
            
            # Topic configuration
            topic_name=config('KAFKA_TOPIC_NAME', default='random-events'),
            partitions=config('KAFKA_PARTITIONS', default=3, cast=int),
            replication_factor=config(
                'KAFKA_REPLICATION_FACTOR', 
                default=1, 
                cast=int
            ),
            
            # Consumer group
            consumer_group_id=config(
                'CONSUMER_GROUP_ID', 
                default='event-processors'
            ),
            
            # Producer settings
            producer_acks=config('PRODUCER_ACKS', default='all'),
            producer_batch_size=config(
                'PRODUCER_BATCH_SIZE', 
                default=1, 
                cast=int
            ),
            producer_linger_ms=config(
                'PRODUCER_LINGER_MS', 
                default=0, 
                cast=int
            ),
            
            # Consumer settings
            consumer_auto_offset_reset=config(
                'CONSUMER_AUTO_OFFSET_RESET', 
                default='earliest'
            ),
            consumer_enable_auto_commit=config(
                'CONSUMER_ENABLE_AUTO_COMMIT', 
                default=True, 
                cast=bool
            ),
            consumer_auto_commit_interval_ms=config(
                'CONSUMER_AUTO_COMMIT_INTERVAL_MS', 
                default=1000, 
                cast=int
            ),
            
            # Application settings
            event_generation_interval=config(
                'EVENT_GENERATION_INTERVAL', 
                default=5, 
                cast=int
            ),
            log_level=config('APP_LOG_LEVEL', default='INFO')
        )
    
    def get_producer_config(self) -> Dict[str, Any]:
        """Get producer configuration dictionary"""
        return {
            'bootstrap_servers': self.config.bootstrap_servers,
            'acks': self.config.producer_acks,
            'batch_size': self.config.producer_batch_size,
            'linger_ms': self.config.producer_linger_ms,
            'key_serializer': lambda x: x.encode('utf-8') if x else None,
            'value_serializer': lambda x: x.encode('utf-8'),
            'retries': 3,
            'retry_backoff_ms': 100,
        }
    
    def get_consumer_config(self) -> Dict[str, Any]:
        """Get consumer configuration dictionary"""
        return {
            'bootstrap_servers': self.config.bootstrap_servers,
            'group_id': self.config.consumer_group_id,
            'auto_offset_reset': self.config.consumer_auto_offset_reset,
            'enable_auto_commit': self.config.consumer_enable_auto_commit,
            'auto_commit_interval_ms': self.config.consumer_auto_commit_interval_ms,
            'key_deserializer': lambda x: x.decode('utf-8') if x else None,
            'value_deserializer': lambda x: x.decode('utf-8'),
            'session_timeout_ms': 30000,
            'heartbeat_interval_ms': 3000,
        }
    
    def get_topic_config(self) -> Dict[str, Any]:
        """Get topic configuration dictionary"""
        return {
            'topic': self.config.topic_name,
            'num_partitions': self.config.partitions,
            'replication_factor': self.config.replication_factor,
        }
    
    def validate_config(self) -> bool:
        """Validate configuration settings"""
        try:
            # Check required settings
            assert self.config.bootstrap_servers, "Bootstrap servers must be set"
            assert self.config.topic_name, "Topic name must be set"
            assert self.config.partitions > 0, "Partitions must be greater than 0"
            assert self.config.replication_factor > 0, "Replication factor must be greater than 0"
            assert self.config.consumer_group_id, "Consumer group ID must be set"
            
            return True
        except AssertionError as e:
            print(f"Configuration validation failed: {e}")
            return False


# Global configuration instance
kafka_config_manager = KafkaConfigManager() 