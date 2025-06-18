#!/usr/bin/env python3
"""
Run Avro Kafka Consumer
Entry point for Avro event consumption with Schema Registry.
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    from consumer.avro_event_consumer import main
    main() 