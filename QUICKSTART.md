# Quick Start Guide - Kafka Assignment

This project provides two implementations:
- **Standard JSON** - Basic Kafka producer/consumer
- **Schema Registry + Avro** - Advanced implementation with data validation

## Standard JSON Implementation

### For Windows Users

```powershell
# 1. Clone repository
git clone https://github.com/arifnrsk/kafka-assignment
cd Assignment Day 24 - Kafka

# 2. Setup environment
make setup

# 3. Start Kafka cluster
make start-kafka

# 4. Run JSON applications (in separate terminals)
make start-producer    # Terminal 1
make start-consumer    # Terminal 2

# 5. Access Kafka UI
# Open browser: http://localhost:8080
```

### For Mac/Linux Users

```bash
# 1. Clone repository
git clone https://github.com/arifnrsk/kafka-assignment
cd Assignment Day 24 - Kafka

# 2. Setup environment
make setup-mac

# 3. Start Kafka cluster
make start-kafka-mac

# 4. Run JSON applications (in separate terminals)
make start-producer-mac    # Terminal 1
make start-consumer-mac    # Terminal 2

# 5. Access Kafka UI
# Open browser: http://localhost:8080
```

## Schema Registry + Avro Implementation

### For Windows Users

```powershell
# 1-3. Follow steps 1-3 from JSON implementation above

# 4. Test Schema Registry setup
make test-avro

# 5. Run Avro applications (in separate terminals)
make start-avro-producer    # Terminal 1
make start-avro-consumer    # Terminal 2

# 6. Access interfaces
# Kafka UI: http://localhost:8080
# Schema Registry: http://localhost:8081
```

### For Mac/Linux Users

```bash
# 1-3. Follow steps 1-3 from JSON implementation above

# 4. Test Schema Registry setup
make test-avro-mac

# 5. Run Avro applications (in separate terminals)
make start-avro-producer-mac    # Terminal 1
make start-avro-consumer-mac    # Terminal 2

# 6. Access interfaces
# Kafka UI: http://localhost:8080
# Schema Registry: http://localhost:8081
```

## Quick Commands Reference

### Windows - JSON Implementation
- `make help` - Show all commands
- `make setup` - Setup virtual environment
- `make start-kafka` - Start Kafka cluster
- `make start-producer` - Start JSON producer
- `make start-consumer` - Start JSON consumer
- `make test` - Run all tests
- `make stop-kafka` - Stop Kafka cluster
- `make status` - Check system status

### Windows - Avro Implementation
- `make test-avro` - Test Schema Registry setup
- `make start-avro-producer` - Start Avro producer
- `make start-avro-consumer` - Start Avro consumer

### Mac/Linux - JSON Implementation
- `make help` - Show all commands
- `make setup-mac` - Setup virtual environment
- `make start-kafka-mac` - Start Kafka cluster
- `make start-producer-mac` - Start JSON producer
- `make start-consumer-mac` - Start JSON consumer
- `make test-mac` - Run all tests
- `make stop-kafka-mac` - Stop Kafka cluster
- `make status` - Check system status

### Mac/Linux - Avro Implementation
- `make test-avro-mac` - Test Schema Registry setup
- `make start-avro-producer-mac` - Start Avro producer
- `make start-avro-consumer-mac` - Start Avro consumer

## Troubleshooting

**Port already in use?**
```bash
# Find process using port
netstat -ano | findstr :9093    # Windows
lsof -i :9093                   # Mac/Linux

# Stop Kafka and restart
make stop-kafka && make start-kafka
```

**Docker issues?**
```bash
# Clean Docker environment
docker-compose down -v
docker system prune -f
make start-kafka
```

## What You'll See

### JSON Implementation:
1. **Producer**: Generates Indonesian events every 5 seconds (JSON format)
2. **Consumer**: Processes events with risk analysis
3. **Kafka UI**: Visual monitoring at http://localhost:8080
4. **Logs**: Real-time processing information

### Avro Implementation:
1. **Avro Producer**: Generates binary Avro events with schema validation
2. **Avro Consumer**: Deserializes and processes Avro events
3. **Schema Registry**: Schema management at http://localhost:8081
4. **Kafka UI**: Enhanced monitoring with schema information
5. **Logs**: Schema-aware processing information

## Assignment Checklist

### Core Requirements:
- Docker Kafka cluster running
- Producer generating events every 5 seconds  
- Consumer processing with analytics
- 3 partitions, 1 replication factor
- Consumer group "event-processors"
- Cross-platform compatibility
- Comprehensive documentation

### Extra Implementation:
- Schema Registry integration
- Avro binary serialization
- Schema evolution support
- Dual implementation (JSON + Avro)
- Enterprise-grade data validation