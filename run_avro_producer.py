#!/usr/bin/env python3
"""
Run Avro Kafka Producer
Entry point for Avro event production with Schema Registry.
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    from producer.avro_event_producer import main
    main() 