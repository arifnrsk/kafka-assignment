#!/usr/bin/env python3
"""
Convenient script to run Kafka Consumer
"""
import sys
import os

# Add src to path
sys.path.append('src')

if __name__ == "__main__":
    print("Starting Kafka Event Consumer...")
    print("=" * 50)
    
    try:
        from consumer.event_consumer import main
        main()
    except KeyboardInterrupt:
        print("\nConsumer stopped by user")
    except Exception as e:
        print(f"Error starting consumer: {e}")
        sys.exit(1) 