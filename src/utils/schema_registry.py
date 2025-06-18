"""
Schema Registry Manager for Kafka Avro Integration
Handles schema registration, retrieval, and management.
"""

import json
import logging
import os
from typing import Dict, Optional, Any
import requests
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer, AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField


class SchemaRegistryManager:
    """
    Manages Avro schemas with Confluent Schema Registry.
    Provides schema registration, serialization, and deserialization capabilities.
    """
    
    def __init__(self, schema_registry_url: str = "http://localhost:8081"):
        """
        Initialize Schema Registry Manager.
        
        Args:
            schema_registry_url: URL of the Schema Registry service
        """
        self.schema_registry_url = schema_registry_url
        self.logger = logging.getLogger(__name__)
        
        # Initialize Schema Registry client
        try:
            self.client = SchemaRegistryClient({'url': schema_registry_url})
            self.logger.info(f"Connected to Schema Registry at {schema_registry_url}")
        except Exception as e:
            self.logger.error(f"Failed to connect to Schema Registry: {str(e)}")
            raise
        
        # Cache for schemas and serializers
        self._schemas: Dict[str, str] = {}
        self._serializers: Dict[str, AvroSerializer] = {}
        self._deserializers: Dict[str, AvroDeserializer] = {}
    
    def load_schema_from_file(self, schema_file_path: str) -> str:
        """
        Load Avro schema from file.
        
        Args:
            schema_file_path: Path to the .avsc schema file
            
        Returns:
            Schema string in JSON format
        """
        try:
            with open(schema_file_path, 'r', encoding='utf-8') as file:
                schema_dict = json.load(file)
                schema_str = json.dumps(schema_dict)
                self.logger.info(f"Loaded schema from {schema_file_path}")
                return schema_str
        except Exception as e:
            self.logger.error(f"Failed to load schema from {schema_file_path}: {str(e)}")
            raise
    
    def register_schema(self, subject: str, schema_str: str) -> int:
        """
        Register schema with Schema Registry.
        
        Args:
            subject: Subject name (typically topic-key or topic-value)
            schema_str: Avro schema as JSON string
            
        Returns:
            Schema ID assigned by registry
        """
        try:
            from confluent_kafka.schema_registry import Schema
            
            # Create schema object
            schema = Schema(schema_str, schema_type="AVRO")
            schema_id = self.client.register_schema(subject, schema)
            
            # Cache the schema
            self._schemas[subject] = schema_str
            
            self.logger.info(f"Registered schema for subject '{subject}' with ID {schema_id}")
            return schema_id
        except Exception as e:
            self.logger.error(f"Failed to register schema for subject '{subject}': {str(e)}")
            raise
    
    def get_schema(self, subject: str, version: str = "latest") -> Optional[str]:
        """
        Get schema from registry by subject and version.
        
        Args:
            subject: Subject name
            version: Schema version (default: "latest")
            
        Returns:
            Schema string or None if not found
        """
        try:
            # Check cache first
            if subject in self._schemas:
                return self._schemas[subject]
            
            # Fetch from registry
            schema = self.client.get_latest_version(subject)
            schema_str = schema.schema.schema_str
            
            # Cache the schema
            self._schemas[subject] = schema_str
            
            self.logger.info(f"Retrieved schema for subject '{subject}' version {version}")
            return schema_str
        except Exception as e:
            self.logger.error(f"Failed to get schema for subject '{subject}': {str(e)}")
            return None
    
    def get_serializer(self, subject: str, schema_str: str) -> AvroSerializer:
        """
        Get or create Avro serializer for a schema.
        
        Args:
            subject: Subject name
            schema_str: Avro schema string
            
        Returns:
            AvroSerializer instance
        """
        if subject in self._serializers:
            return self._serializers[subject]
        
        try:
            serializer = AvroSerializer(
                schema_registry_client=self.client,
                schema_str=schema_str,
                to_dict=self._to_dict
            )
            
            # Cache the serializer
            self._serializers[subject] = serializer
            
            self.logger.info(f"Created serializer for subject '{subject}'")
            return serializer
        except Exception as e:
            self.logger.error(f"Failed to create serializer for subject '{subject}': {str(e)}")
            raise
    
    def get_deserializer(self, subject: str, schema_str: str) -> AvroDeserializer:
        """
        Get or create Avro deserializer for a schema.
        
        Args:
            subject: Subject name
            schema_str: Avro schema string
            
        Returns:
            AvroDeserializer instance
        """
        if subject in self._deserializers:
            return self._deserializers[subject]
        
        try:
            deserializer = AvroDeserializer(
                schema_registry_client=self.client,
                schema_str=schema_str,
                from_dict=self._from_dict
            )
            
            # Cache the deserializer
            self._deserializers[subject] = deserializer
            
            self.logger.info(f"Created deserializer for subject '{subject}'")
            return deserializer
        except Exception as e:
            self.logger.error(f"Failed to create deserializer for subject '{subject}': {str(e)}")
            raise
    
    def serialize_event(self, subject: str, event_data: Dict[str, Any]) -> bytes:
        """
        Serialize event data using Avro schema.
        
        Args:
            subject: Subject name
            event_data: Event data dictionary
            
        Returns:
            Serialized bytes
        """
        try:
            if subject not in self._serializers:
                schema_str = self.get_schema(subject)
                if not schema_str:
                    raise ValueError(f"Schema not found for subject '{subject}'")
                self.get_serializer(subject, schema_str)
            
            serializer = self._serializers[subject]
            ctx = SerializationContext(subject, MessageField.VALUE)
            
            serialized_data = serializer(event_data, ctx)
            self.logger.debug(f"Serialized event for subject '{subject}'")
            return serialized_data
        except Exception as e:
            self.logger.error(f"Failed to serialize event for subject '{subject}': {str(e)}")
            raise
    
    def deserialize_event(self, subject: str, serialized_data: bytes) -> Dict[str, Any]:
        """
        Deserialize event data using Avro schema.
        
        Args:
            subject: Subject name
            serialized_data: Serialized bytes
            
        Returns:
            Deserialized event data dictionary
        """
        try:
            if subject not in self._deserializers:
                schema_str = self.get_schema(subject)
                if not schema_str:
                    raise ValueError(f"Schema not found for subject '{subject}'")
                self.get_deserializer(subject, schema_str)
            
            deserializer = self._deserializers[subject]
            ctx = SerializationContext(subject, MessageField.VALUE)
            
            event_data = deserializer(serialized_data, ctx)
            self.logger.debug(f"Deserialized event for subject '{subject}'")
            return event_data
        except Exception as e:
            self.logger.error(f"Failed to deserialize event for subject '{subject}': {str(e)}")
            raise
    
    def list_subjects(self) -> list:
        """
        List all registered subjects in Schema Registry.
        
        Returns:
            List of subject names
        """
        try:
            subjects = self.client.get_subjects()
            self.logger.info(f"Found {len(subjects)} subjects in registry")
            return subjects
        except Exception as e:
            self.logger.error(f"Failed to list subjects: {str(e)}")
            return []
    
    def health_check(self) -> bool:
        """
        Check if Schema Registry is healthy and accessible.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            response = requests.get(f"{self.schema_registry_url}/subjects", timeout=5)
            if response.status_code == 200:
                self.logger.info("Schema Registry health check passed")
                return True
            else:
                self.logger.warning(f"Schema Registry health check failed: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"Schema Registry health check failed: {str(e)}")
            return False
    
    @staticmethod
    def _to_dict(event_data: Dict[str, Any], ctx: SerializationContext) -> Dict[str, Any]:
        """
        Convert event data to dictionary for serialization.
        This is a pass-through since our data is already in dict format.
        """
        return event_data
    
    @staticmethod
    def _from_dict(event_data: Dict[str, Any], ctx: SerializationContext) -> Dict[str, Any]:
        """
        Convert dictionary to event data after deserialization.
        This is a pass-through since we want to keep dict format.
        """
        return event_data


def create_schema_registry_manager(schema_registry_url: str = None) -> SchemaRegistryManager:
    """
    Factory function to create Schema Registry Manager.
    
    Args:
        schema_registry_url: Optional URL override
        
    Returns:
        SchemaRegistryManager instance
    """
    if not schema_registry_url:
        schema_registry_url = os.getenv("SCHEMA_REGISTRY_URL", "http://localhost:8081")
    
    return SchemaRegistryManager(schema_registry_url)


# Example usage and testing
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Create manager
    manager = create_schema_registry_manager()
    
    # Test health check
    if manager.health_check():
        print("Schema Registry is healthy!")
        
        # List existing subjects
        subjects = manager.list_subjects()
        print(f"Existing subjects: {subjects}")
    else:
        print("Schema Registry is not accessible!") 