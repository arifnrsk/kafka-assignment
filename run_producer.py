#!/usr/bin/env python3
"""
Convenient script to run Kafka Producer
"""
import sys
import os

# Add src to path
sys.path.append('src')

if __name__ == "__main__":
    print("Starting Kafka Event Producer...")
    print("=" * 50)
    
    try:
        from producer.event_producer import main
        main()
    except KeyboardInterrupt:
        print("\nProducer stopped by user")
    except Exception as e:
        print(f"Error starting producer: {e}")
        sys.exit(1) 