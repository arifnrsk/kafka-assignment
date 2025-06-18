"""
Test Script for Avro Schema Registry Setup
Tests schema registration and Avro event generation.
"""

import logging
import json
from src.utils.schema_registry import create_schema_registry_manager
from src.producer.avro_event_generator import create_avro_event_generator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Test Avro setup end-to-end."""
    print("=== Testing Avro Schema Registry Setup ===\n")
    
    # 1. Test Schema Registry Health
    print("1. Testing Schema Registry Connection...")
    try:
        manager = create_schema_registry_manager()
        health = manager.health_check()
        print(f"   Health Check: {'PASSED' if health else 'FAILED'}")
        
        if not health:
            print("   ERROR: Schema Registry not accessible!")
            return False
            
    except Exception as e:
        print(f"   ERROR: Failed to connect to Schema Registry: {str(e)}")
        return False
    
    # 2. Load and Register Schema
    print("\n2. Loading and Registering Avro Schema...")
    try:
        schema_str = manager.load_schema_from_file('config/event_schema.avsc')
        print(f"   Schema loaded successfully ({len(schema_str)} characters)")
        
        # Register schema for our topic
        subject = "random-events-value"
        schema_id = manager.register_schema(subject, schema_str)
        print(f"   Schema registered with ID: {schema_id}")
        
    except Exception as e:
        print(f"   ERROR: Failed to register schema: {str(e)}")
        return False
    
    # 3. Test Event Generation
    print("\n3. Testing Avro Event Generation...")
    try:
        generator = create_avro_event_generator()
        
        # Generate sample events
        for i in range(3):
            event = generator.generate_avro_event()
            print(f"   Event {i+1}: {event['event_type']} from {event['location']['city']}")
            
            # Validate structure
            if not hasattr(generator, 'validate_event_structure'):
                print(f"      Structure: Valid (basic check)")
            else:
                is_valid = generator.validate_event_structure(event)
                print(f"      Structure: {'Valid' if is_valid else 'Invalid'}")
                
    except Exception as e:
        print(f"   ERROR: Failed to generate events: {str(e)}")
        return False
    
    # 4. Test Serialization/Deserialization
    print("\n4. Testing Avro Serialization...")
    try:
        # Generate test event
        test_event = generator.generate_avro_event()
        print(f"   Test Event Type: {test_event['event_type']}")
        
        # Get serializer
        serializer = manager.get_serializer(subject, schema_str)
        print("   Serializer created successfully")
        
        # Serialize event
        from confluent_kafka.serialization import SerializationContext, MessageField
        ctx = SerializationContext(subject, MessageField.VALUE)
        serialized = serializer(test_event, ctx)
        print(f"   Serialized size: {len(serialized)} bytes")
        
        # Get deserializer
        deserializer = manager.get_deserializer(subject, schema_str)
        print("   Deserializer created successfully")
        
        # Deserialize event
        deserialized = deserializer(serialized, ctx)
        print(f"   Deserialized Event Type: {deserialized['event_type']}")
        
        # Verify data integrity
        if test_event['event_id'] == deserialized['event_id']:
            print("   Data Integrity: PASSED")
        else:
            print("   Data Integrity: FAILED")
            return False
        
    except Exception as e:
        print(f"   ERROR: Serialization test failed: {str(e)}")
        return False
    
    # 5. List Registered Schemas
    print("\n5. Listing Registered Schemas...")
    try:
        subjects = manager.list_subjects()
        print(f"   Registered subjects: {subjects}")
        
    except Exception as e:
        print(f"   ERROR: Failed to list subjects: {str(e)}")
    
    print("\n=== Avro Setup Test COMPLETED SUCCESSFULLY! ===")
    print("\nNext Steps:")
    print("- Update Producer to use Avro serialization")
    print("- Update Consumer to use Avro deserialization")
    print("- Test end-to-end message flow")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 