# Kafka Event Streaming System
> **Kafka Producer-Consumer Implementation with Docker and Schema Registry**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Kafka](https://img.shields.io/badge/Apache%20Kafka-3.4-orange.svg)](https://kafka.apache.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docker.com)
[![Avro](https://img.shields.io/badge/Apache%20Avro-Schema%20Registry-brightgreen.svg)](https://avro.apache.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Assignment Objectives

This project implements a complete Kafka event streaming system with the following requirements:

### Core Requirements
1. **Docker-based Kafka Cluster** - Zookeeper, Broker, and UI
2. **Event Producer** - Generates random Indonesian events every 5 seconds
3. **Event Consumer** - Processes events with advanced analytics and risk scoring
4. **Partitioning Strategy** - 3 partitions with 1 replication factor
5. **Consumer Groups** - Implements "event-processors" consumer group

### Extra Implementation: Schema Registry with Avro
6. **Schema Registry** - Centralized schema management and evolution
7. **Avro Serialization** - Binary format for efficient data transmission
8. **Schema Evolution** - Backward and forward compatibility support
9. **Dual Implementation** - Both JSON and Avro versions available

## Architecture Overview

### Standard JSON Implementation
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Producer      │───▶│  Kafka Cluster  │───▶│   Consumer      │
│                 │    │                 │    │                 │
│ • Event Gen     │    │ • 3 Partitions  │    │ • Risk Analysis │
│ • 5s Interval   │    │ • Replication=1 │    │ • Alerts        │
│ • JSON Format   │    │ • UI Dashboard  │    │ • Statistics    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Schema Registry + Avro Implementation
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Avro Producer   │───▶│ Schema Registry │───▶│  Kafka Cluster  │───▶│ Avro Consumer   │
│                 │    │                 │    │                 │    │                 │
│ • Event Gen     │    │ • Schema Mgmt   │    │ • 3 Partitions  │    │ • Risk Analysis │
│ • 5s Interval   │    │ • Evolution     │    │ • Replication=1 │    │ • Alerts        │
│ • Avro Binary   │    │ • Validation    │    │ • UI Dashboard  │    │ • Statistics    │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Project Structure

```
Assignment Day 24 - Kafka/
├── docker/
│   └── docker-compose.yml          # Complete Kafka ecosystem
├── src/
│   ├── producer/
│   │   ├── event_producer.py       # Main JSON producer with connection handling
│   │   ├── event_generator.py      # Random Indonesian event generator
│   │   ├── avro_event_producer.py  # Avro producer with Schema Registry
│   │   └── avro_event_generator.py # Avro-compatible event generator
│   ├── consumer/
│   │   ├── event_consumer.py       # Main JSON consumer with graceful shutdown
│   │   ├── avro_event_consumer.py  # Avro consumer with Schema Registry
│   │   └── processor.py            # Advanced event processing & analytics
│   └── utils/
│       ├── kafka_config.py         # Centralized configuration management
│       ├── schema_registry.py      # Schema Registry integration
│       └── logger.py               # Centralized logging setup
├── config/
│   ├── kafka_topics.json           # Topic configuration definitions
│   └── event_schema.avsc           # Avro schema definition
├── tests/
│   ├── test_producer.py            # Producer unit tests
│   └── test_consumer.py            # Consumer unit tests
├── logs/                           # Application logs directory
├── run_producer.py                 # JSON producer entry point
├── run_consumer.py                 # JSON consumer entry point
├── run_avro_producer.py            # Avro producer entry point
├── run_avro_consumer.py            # Avro consumer entry point
├── test_avro_setup.py              # Avro Schema Registry test
├── Makefile                        # Cross-platform automation commands
├── requirements.txt                # Python dependencies
└── README.md                       # This documentation
```

## Quick Start

### Prerequisites
- Python 3.8+
- Docker & Docker Compose
- Git

### Option 1: Automated Setup (Recommended)

**For Windows:**
```powershell
# Clone and setup
git clone https://github.com/arifnrsk/kafka-assignment
cd Assignment Day 24 - Kafka

# Complete setup and start
make setup
make start-kafka
```

**For Mac/Linux:**
```bash
# Clone and setup
git clone https://github.com/arifnrsk/kafka-assignment
cd Assignment Day 24 - Kafka

# Complete setup and start
make setup-mac
make start-kafka-mac
```

### Option 2: Manual Setup

**Windows:**
```powershell
# 1. Setup virtual environment
python -m venv venv
venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start Kafka cluster
cd docker && docker-compose up -d

# 4. Run applications
python run_producer.py  # Terminal 1
python run_consumer.py  # Terminal 2
```

**Mac/Linux:**
```bash
# 1. Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start Kafka cluster
cd docker && docker-compose up -d

# 4. Run applications
python3 run_producer.py  # Terminal 1
python3 run_consumer.py  # Terminal 2
```

## Cross-Platform Commands

### Windows Commands

**JSON Implementation (Standard):**
```powershell
make setup              # Setup virtual environment
make start-kafka        # Start Kafka cluster
make start-producer     # Start JSON event producer
make start-consumer     # Start JSON event consumer
make test              # Run all tests
make stop-kafka        # Stop Kafka cluster
```

**Avro Implementation (Schema Registry):**
```powershell
make start-avro-producer # Start Avro event producer
make start-avro-consumer # Start Avro event consumer
make test-avro          # Test Avro Schema Registry setup
```

### Mac/Linux Commands

**JSON Implementation (Standard):**
```bash
make setup-mac          # Setup virtual environment
make start-kafka-mac    # Start Kafka cluster
make start-producer-mac # Start JSON event producer
make start-consumer-mac # Start JSON event consumer
make test-mac          # Run all tests
make stop-kafka-mac    # Stop Kafka cluster
```

**Avro Implementation (Schema Registry):**
```bash
make start-avro-producer-mac # Start Avro event producer
make start-avro-consumer-mac # Start Avro event consumer
make test-avro-mac          # Test Avro Schema Registry setup
```

## Kafka UI Dashboard

Access the web-based Kafka management interface:

**URL**: `http://localhost:8080`

### Features Available:
- **Real-time Monitoring** - Message throughput and consumer lag
- **Topic Management** - Create, configure, and monitor topics
- **Message Browser** - View and search individual messages
- **Consumer Groups** - Monitor consumer group health and rebalancing
- **Schema Registry** - Message schema management

## Schema Registry Implementation

This project includes an advanced implementation using Confluent Schema Registry with Apache Avro for enterprise-grade data serialization.

### Benefits of Schema Registry + Avro:
- **Schema Evolution** - Add, remove, or modify fields without breaking consumers
- **Data Validation** - Automatic validation of message structure
- **Compact Binary Format** - Smaller message size compared to JSON
- **Type Safety** - Strong typing with automatic serialization/deserialization
- **Centralized Management** - Single source of truth for data schemas

### Schema Registry Endpoints:
- **Schema Registry API**: `http://localhost:8081`
- **Health Check**: `http://localhost:8081/subjects`

### Getting Started with Avro:

1. **Test Schema Registry Setup:**

**Windows:**
```powershell
python test_avro_setup.py
```

**Mac/Linux:**
```bash
python3 test_avro_setup.py
```

2. **Start Avro Producer & Consumer:**

**Windows:**
```powershell
# Terminal 1: Start Avro Producer
make start-avro-producer

# Terminal 2: Start Avro Consumer  
make start-avro-consumer
```

**Mac/Linux:**
```bash
# Terminal 1: Start Avro Producer
make start-avro-producer-mac

# Terminal 2: Start Avro Consumer  
make start-avro-consumer-mac
```

3. **View Schema in Registry:**

**Windows:**
```powershell
# List all subjects
curl http://localhost:8081/subjects

# Get schema for topic
curl http://localhost:8081/subjects/random-events-value/versions/latest
```

**Mac/Linux:**
```bash
# List all subjects
curl http://localhost:8081/subjects

# Get schema for topic
curl http://localhost:8081/subjects/random-events-value/versions/latest
```

### Avro Schema Structure:
The event schema (`config/event_schema.avsc`) includes:
- **Event Metadata** - ID, type, timestamp, user information
- **Location Data** - Indonesian cities with provinces
- **Device Information** - Type, OS, browser details
- **Event Data** - Type-specific data with validation
- **Metadata** - Source, environment, processing information

## Configuration Details

### Kafka Cluster Configuration
```yaml
# docker/docker-compose.yml
Topic: random-events
Partitions: 3
Replication Factor: 1
Retention: 24 hours
Consumer Group: event-processors
```

### Producer Configuration
```python
# src/utils/kafka_config.py - Producer Settings
bootstrap_servers: localhost:9093
acks: all                    # Wait for all replicas
batch_size: 1               # Send immediately
event_interval: 5 seconds   # Generation frequency
serialization: UTF-8        # String encoding
```

### Consumer Configuration
```python
# src/utils/kafka_config.py - Consumer Settings
bootstrap_servers: localhost:9093
group_id: event-processors
auto_offset_reset: earliest  # Start from beginning
enable_auto_commit: true    # Automatic offset commits
session_timeout: 30s        # Consumer health timeout
```

## Code Architecture Explained

### 1. Event Producer (`src/producer/event_producer.py`)

**Core Functionality:**
```python
class KafkaEventProducer:
    def __init__(self):
        # Configuration management
        self.config_manager = kafka_config_manager
        self.logger = producer_logger
        self.generator = EventGenerator()
        
    def _create_producer(self) -> KafkaProducer:
        # Creates producer with error handling and retries
        # Implements connection validation
        # Configures serializers for key/value
        
    def start_producing(self):
        # Main production loop with 5-second intervals
        # Graceful shutdown handling (Ctrl+C)
        # Error recovery and reconnection logic
```

**Key Features:**
- **Graceful Shutdown** - Signal handling for clean termination
- **Error Recovery** - Automatic reconnection on failures
- **Random Data Generation** - Indonesian cities, realistic values
- **Partition Distribution** - Automatic load balancing across partitions

### 2. Event Consumer (`src/consumer/event_consumer.py`)

**Core Functionality:**
```python
class KafkaEventConsumer:
    def __init__(self):
        # Multi-component initialization
        self.processor = EventProcessor()  # Advanced analytics
        self.consumer = None
        self.running = False
        
    def _process_message(self, message):
        # Message deserialization and validation
        # Event data extraction and parsing
        # Risk analysis and alert generation
        # Statistics tracking and logging
```

**Key Features:**
- **Advanced Processing** - Risk scoring, value categorization
- **Alert System** - High-risk transaction detection
- **Statistics Tracking** - Real-time consumption metrics
- **Consumer Group Management** - Automatic partition assignment

### 3. Event Processor (`src/consumer/processor.py`)

**Analytics Engine:**
```python
class EventProcessor:
    def process_event(self, event_data: str) -> ProcessingResult:
        # Risk Score Calculation
        risk_score = self._calculate_risk_score(event)
        
        # Value Categorization
        value_category = self._categorize_value(event.get('value', 0))
        
        # Alert Generation
        alerts = self._generate_alerts(event, risk_score)
        
        # Statistics Update
        self._update_statistics(event)
```

**Risk Analysis Logic:**
- **High Risk (1.0)**: Error events, failed transactions
- **Medium Risk (0.5-0.9)**: High-value transactions, suspicious patterns
- **Low Risk (0.1-0.4)**: Normal operational events

### 4. Configuration Management (`src/utils/kafka_config.py`)

**Centralized Configuration:**
```python
class KafkaConfigManager:
    def __init__(self):
        # Environment variable loading with defaults
        # Validation and error checking
        # Cross-environment compatibility
        
    def get_producer_config(self) -> Dict[str, Any]:
        # Producer-specific settings
        # Serializer configuration
        # Performance tuning parameters
        
    def get_consumer_config(self) -> Dict[str, Any]:
        # Consumer-specific settings
        # Deserializer configuration
        # Consumer group settings
```

## Event Data Schema

### Generated Event Structure
```json
{
  "event_id": "uuid4-string",
  "event_type": "user_login|purchase|api_call|error|...",
  "user_id": 1234,
  "timestamp": "2024-06-18T10:30:45Z",
  "value": 750.50,
  "status": "success|pending|failed|cancelled",
  "location": {
    "city": "Jakarta|Surabaya|Bandung|...",
    "country": "Indonesia"
  },
  "device_type": "mobile|desktop|tablet|smart_tv|iot_device",
  "metadata": {
    "session_id": "session-uuid",
    "ip_address": "192.168.1.xxx",
    "user_agent": "browser-info"
  }
}
```

### Event Types Generated
- **user_login** / **user_logout** - Authentication events
- **purchase** / **add_to_cart** / **remove_from_cart** - E-commerce actions
- **page_view** / **click** / **form_submit** - User interactions
- **search** / **api_call** - System operations
- **error** / **session_timeout** - System events

## Testing

### Run All Tests
```bash
# Windows
make test

# Mac/Linux
make test-mac
```

### Individual Component Testing

**Windows:**
```powershell
# Test producer only
python tests/test_producer.py

# Test consumer only
python tests/test_consumer.py

# Test with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

**Mac/Linux:**
```bash
# Test producer only
python3 tests/test_producer.py

# Test consumer only
python3 tests/test_consumer.py

# Test with coverage
python3 -m pytest tests/ --cov=src --cov-report=html
```

### Test Coverage Areas
- **Producer Connection** - Kafka connectivity and error handling
- **Event Generation** - Data validation and schema compliance
- **Consumer Processing** - Message parsing and analytics
- **Configuration Loading** - Environment variable handling
- **Error Scenarios** - Network failures and recovery

## Monitoring & Observability

### Application Logs

**Windows:**
```powershell
# View real-time logs (use Get-Content for tail equivalent)
Get-Content logs/producer.log -Wait    # Producer activity
Get-Content logs/consumer.log -Wait    # Consumer processing
Get-Content logs/application.log -Wait # General application logs
```

**Mac/Linux:**
```bash
# View real-time logs
tail -f logs/producer.log    # Producer activity
tail -f logs/consumer.log    # Consumer processing
tail -f logs/application.log # General application logs
```

### Docker Container Logs
```bash
# Kafka broker logs
docker logs kafka-broker -f

# Zookeeper logs
docker logs kafka-zookeeper -f

# All services
make logs
```

### Key Metrics to Monitor
- **Producer Throughput**: Messages/second sent
- **Consumer Lag**: Messages pending processing
- **Error Rate**: Failed message processing percentage
- **Risk Alerts**: High-risk event detection count

## Development Workflow

### 1. Development Setup
```bash
make dev-setup    # Complete development environment
```

### 2. Code Quality
```bash
make lint         # Code linting with flake8
make format       # Code formatting with black & isort
```

### 3. Testing Workflow
```bash
make full-test    # Complete test cycle with cleanup
```

### 4. Production Deployment
```bash
make build        # Build production images
make deploy       # Deploy to production environment
```

## Troubleshooting

### Common Issues

**1. Kafka Connection Failed**
```bash
# Check if Kafka is running
docker ps | grep kafka

# Restart Kafka cluster
make stop-kafka && make start-kafka
```

**2. Consumer Lag Issues**
```bash
# Check consumer group status
kafka-consumer-groups.sh --bootstrap-server localhost:9093 --describe --group event-processors
```

**3. Port Already in Use**

**Windows:**
```powershell
# Find and kill process using port 9093
netstat -ano | findstr :9093
taskkill /PID <process-id> /F
```

**Mac/Linux:**
```bash
# Find and kill process using port 9093
lsof -i :9093
kill -9 <process-id>
```

**4. Docker Issues**
```bash
# Clean Docker environment
docker-compose down -v
docker system prune -f
make start-kafka
```

## Kafka Concepts Implemented
- **Topics & Partitions** - Message organization and parallelism
- **Producer/Consumer API** - Application integration patterns
- **Consumer Groups** - Load balancing and fault tolerance
- **Serialization** - Data format handling
- **Offset Management** - Message delivery guarantees

## Advanced Features Used
- **Schema Registry** - Message schema evolution
- **Kafka UI** - Visual monitoring and management
- **Docker Compose** - Container orchestration
- **Health Checks** - Service reliability monitoring

## Assignment Completion Checklist

- **Docker Kafka Cluster** - Zookeeper + Broker + UI
- **Producer Implementation** - 5-second interval event generation
- **Consumer Implementation** - Advanced event processing
- **Partitioning** - 3 partitions configured
- **Replication** - 1 replica factor set
- **Consumer Groups** - "event-processors" group implemented
- **Error Handling** - Comprehensive error management
- **Logging** - Professional logging setup
- **Testing** - Unit tests for all components
- **Documentation** - Complete README with examples
- **Cross-Platform** - Windows/Mac/Linux compatibility

---