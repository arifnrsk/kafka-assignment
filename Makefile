# Makefile for Kafka Assignment - Cross Platform Support
.PHONY: help setup setup-mac start-kafka start-kafka-mac stop-kafka stop-kafka-mac start-producer start-producer-mac start-consumer start-consumer-mac test test-mac clean lint format install

# Default target
help:
	@echo "Kafka Assignment Commands (Cross-Platform):"
	@echo ""
	@echo "=== WINDOWS COMMANDS ==="
	@echo "  setup          - Setup virtual environment and install dependencies"
	@echo "  install        - Install dependencies"
	@echo "  start-kafka    - Start Kafka cluster with Docker"
	@echo "  stop-kafka     - Stop Kafka cluster"
	@echo "  start-producer - Start Kafka producer"
	@echo "  start-consumer - Start Kafka consumer"
	@echo "  test           - Run tests"
	@echo "  test-producer  - Test producer only"
	@echo "  test-consumer  - Test consumer only"
	@echo ""
	@echo "=== MAC/LINUX COMMANDS ==="
	@echo "  setup-mac      - Setup virtual environment and install dependencies (Mac/Linux)"
	@echo "  start-kafka-mac - Start Kafka cluster with Docker (Mac/Linux)"
	@echo "  stop-kafka-mac - Stop Kafka cluster (Mac/Linux)"
	@echo "  start-producer-mac - Start Kafka producer (Mac/Linux)"
	@echo "  start-consumer-mac - Start Kafka consumer (Mac/Linux)"
	@echo "  test-mac       - Run tests (Mac/Linux)"
	@echo ""
	@echo "=== UNIVERSAL COMMANDS ==="
	@echo "  lint           - Run linting checks"
	@echo "  format         - Format code with black and isort"
	@echo "  clean          - Clean up temporary files"
	@echo "  logs           - Show Kafka logs"

# ============================================
# WINDOWS COMMANDS
# ============================================

# Setup virtual environment (Windows)
setup:
	@echo "Setting up virtual environment for Windows..."
	python -m venv venv
	@echo "Installing dependencies in virtual environment..."
	venv\Scripts\python.exe -m pip install --upgrade pip
	venv\Scripts\python.exe -m pip install -r requirements.txt
	@echo "Setup complete! Activate with: venv\\Scripts\\activate"

# Install dependencies (Windows)
install:
	@echo "Installing dependencies..."
	pip install --upgrade pip
	pip install -r requirements.txt
	@echo "Dependencies installed!"

# Docker commands (Windows)
start-kafka:
	@echo "Starting Kafka cluster (Windows)..."
	cd docker && docker-compose up -d
	@echo "Waiting for services to be ready..."
	@ping -n 11 127.0.0.1 >nul 2>&1
	@echo "Kafka cluster is running!"
	@echo "Kafka UI: http://localhost:8080"
	@echo "Kafka Broker: localhost:9093"

stop-kafka:
	@echo "Stopping Kafka cluster (Windows)..."
	cd docker && docker-compose down
	@echo "Kafka cluster stopped!"

# Application commands (Windows)
start-producer:
	@echo "Starting Kafka Producer (Windows)..."
	python run_producer.py

start-consumer:
	@echo "Starting Kafka Consumer (Windows)..."
	python run_consumer.py

# Avro commands (Windows)
start-avro-producer:
	@echo "Starting Avro Kafka Producer with Schema Registry..."
	python run_avro_producer.py

start-avro-consumer:
	@echo "Starting Avro Kafka Consumer with Schema Registry..."
	python run_avro_consumer.py

test-avro:
	@echo "Testing Avro Schema Registry setup..."
	python test_avro_setup.py

# Testing commands (Windows)
test:
	@echo "Running all tests (Windows)..."
	python -m pytest tests/ -v --tb=short

test-producer:
	@echo "Testing producer (Windows)..."
	python tests/test_producer.py
	python -m pytest tests/test_producer.py -v

test-consumer:
	@echo "Testing consumer (Windows)..."
	python tests/test_consumer.py
	python -m pytest tests/test_consumer.py -v

# ============================================
# MAC/LINUX COMMANDS
# ============================================

# Setup virtual environment (Mac/Linux)
setup-mac:
	@echo "Setting up virtual environment for Mac/Linux..."
	python3 -m venv venv
	@echo "Installing dependencies in virtual environment..."
	venv/bin/python -m pip install --upgrade pip
	venv/bin/python -m pip install -r requirements.txt
	@echo "Setup complete! Activate with: source venv/bin/activate"

# Docker commands (Mac/Linux)
start-kafka-mac:
	@echo "Starting Kafka cluster (Mac/Linux)..."
	cd docker && docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 10
	@echo "Kafka cluster is running!"
	@echo "Kafka UI: http://localhost:8080"
	@echo "Kafka Broker: localhost:9093"

stop-kafka-mac:
	@echo "Stopping Kafka cluster (Mac/Linux)..."
	cd docker && docker-compose down
	@echo "Kafka cluster stopped!"

# Application commands (Mac/Linux)
start-producer-mac:
	@echo "Starting Kafka Producer (Mac/Linux)..."
	python3 run_producer.py

start-consumer-mac:
	@echo "Starting Kafka Consumer (Mac/Linux)..."
	python3 run_consumer.py

# Avro commands (Mac/Linux)
start-avro-producer-mac:
	@echo "Starting Avro Kafka Producer with Schema Registry..."
	python3 run_avro_producer.py

start-avro-consumer-mac:
	@echo "Starting Avro Kafka Consumer with Schema Registry..."
	python3 run_avro_consumer.py

test-avro-mac:
	@echo "Testing Avro Schema Registry setup..."
	python3 test_avro_setup.py

# Testing commands (Mac/Linux)
test-mac:
	@echo "Running all tests (Mac/Linux)..."
	python3 -m pytest tests/ -v --tb=short

test-producer-mac:
	@echo "Testing producer (Mac/Linux)..."
	python3 tests/test_producer.py
	python3 -m pytest tests/test_producer.py -v

test-consumer-mac:
	@echo "Testing consumer (Mac/Linux)..."
	python3 tests/test_consumer.py
	python3 -m pytest tests/test_consumer.py -v

# ============================================
# UNIVERSAL COMMANDS (Work on all platforms)
# ============================================

# Code quality commands
lint:
	@echo "Running linting checks..."
	flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503
	@echo "Linting passed!"

format:
	@echo "Formatting code..."
	black src/ tests/ *.py --line-length=88
	isort src/ tests/ *.py --profile black
	@echo "Code formatted!"

# Utility commands
clean:
	@echo "Cleaning up..."
	@echo "Removing Python cache files..."
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "__pycache__" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	@echo "Removing build artifacts..."
	rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/ 2>/dev/null || true
	@echo "Cleanup complete!"

logs:
	@echo "Showing Kafka logs..."
	cd docker && docker-compose logs -f --tail=50

# ============================================
# ADVANCED WORKFLOW COMMANDS
# ============================================

# Development workflow (Windows)
dev-setup: setup start-kafka
	@echo "Development environment ready (Windows)!"
	@echo "Next steps:"
	@echo "   1. Activate venv: venv\\Scripts\\activate"
	@echo "   2. Producer: make start-producer"
	@echo "   3. Consumer: make start-consumer"
	@echo "   4. Kafka UI: http://localhost:8080"

# Development workflow (Mac/Linux)
dev-setup-mac: setup-mac start-kafka-mac
	@echo "Development environment ready (Mac/Linux)!"
	@echo "Next steps:"
	@echo "   1. Activate venv: source venv/bin/activate"
	@echo "   2. Producer: make start-producer-mac"
	@echo "   3. Consumer: make start-consumer-mac"
	@echo "   4. Kafka UI: http://localhost:8080"

# Full workflow test (Windows)
full-test: start-kafka test stop-kafka
	@echo "Full test workflow complete (Windows)!"

# Full workflow test (Mac/Linux)
full-test-mac: start-kafka-mac test-mac stop-kafka-mac
	@echo "Full test workflow complete (Mac/Linux)!"

# Quick development commands (Windows)
run: start-kafka
	@echo "Starting both producer and consumer (Windows)..."
	@echo "Starting producer in background..."
	@start /B python run_producer.py
	@ping -n 4 127.0.0.1 >nul 2>&1
	@echo "Starting consumer..."
	python run_consumer.py

# Quick development commands (Mac/Linux)
run-mac: start-kafka-mac
	@echo "Starting both producer and consumer (Mac/Linux)..."
	@echo "Starting producer in background..."
	@python3 run_producer.py &
	@sleep 3
	@echo "Starting consumer..."
	python3 run_consumer.py

# ============================================
# MONITORING & DEBUGGING
# ============================================

# Check system status
status:
	@echo "=== SYSTEM STATUS ==="
	@echo "Docker containers:"
	@docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
	@echo ""
	@echo "Kafka topics:"
	@docker exec kafka-broker kafka-topics.sh --bootstrap-server localhost:9092 --list 2>/dev/null || echo "Kafka not running"
	@echo ""
	@echo "Consumer groups:"
	@docker exec kafka-broker kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list 2>/dev/null || echo "Kafka not running"

# Monitor consumer lag
monitor-lag:
	@echo "=== CONSUMER LAG MONITORING ==="
	@docker exec kafka-broker kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group event-processors 2>/dev/null || echo "Consumer group not found"

# Reset consumer offsets (use with caution)
reset-offsets:
	@echo "WARNING: This will reset consumer offsets to earliest!"
	@echo "Press Ctrl+C to cancel, or wait 5 seconds to continue..."
	@sleep 5
	@docker exec kafka-broker kafka-consumer-groups.sh --bootstrap-server localhost:9092 --group event-processors --reset-offsets --to-earliest --topic random-events --execute

# ============================================
# PRODUCTION DEPLOYMENT
# ============================================

# Build production images
build:
	@echo "Building production Docker images..."
	@docker build -t kafka-producer:latest -f docker/Dockerfile.producer .
	@docker build -t kafka-consumer:latest -f docker/Dockerfile.consumer .
	@echo "Production images built!"

# Deploy to production
deploy:
	@echo "Deploying to production environment..."
	@echo "This would typically involve:"
	@echo "  1. Pushing images to registry"
	@echo "  2. Updating Kubernetes/Docker Swarm configs"
	@echo "  3. Rolling deployment"
	@echo "Not implemented in this demo version."

# Health check
health:
	@echo "=== HEALTH CHECK ==="
	@echo "Checking Kafka broker health..."
	@curl -s http://localhost:8080/api/clusters/local-kafka/brokers 2>/dev/null | grep -q "localhost" && echo "SUCCESS: Kafka UI accessible" || echo "ERROR: Kafka UI not accessible"
	@docker exec kafka-broker kafka-broker-api-versions.sh --bootstrap-server localhost:9092 >/dev/null 2>&1 && echo "SUCCESS: Kafka broker healthy" || echo "ERROR: Kafka broker unhealthy"
	@echo "Checking topic existence..."
	@docker exec kafka-broker kafka-topics.sh --bootstrap-server localhost:9092 --list 2>/dev/null | grep -q "random-events" && echo "SUCCESS: Topic 'random-events' exists" || echo "ERROR: Topic 'random-events' not found"

# Performance test
perf-test:
	@echo "Running Kafka performance test..."
	@echo "Producer performance test (10000 messages):"
	@docker exec kafka-broker kafka-producer-perf-test.sh --topic random-events --num-records 10000 --record-size 1024 --throughput 1000 --producer-props bootstrap.servers=localhost:9092
	@echo ""
	@echo "Consumer performance test:"
	@docker exec kafka-broker kafka-consumer-perf-test.sh --topic random-events --messages 10000 --bootstrap-server localhost:9092

# ============================================
# DOCUMENTATION
# ============================================

# Generate documentation
docs:
	@echo "Generating project documentation..."
	@mkdir -p docs
	@echo "# Project Documentation" > docs/README.md
	@echo "Documentation generated in docs/ directory"

# Show project info
info:
	@echo "=== PROJECT INFORMATION ==="
	@echo "Project: Kafka Event Streaming System"
	@echo "Version: 1.0.0"
	@echo "Author: Data Engineering Bootcamp"
	@echo "Python Version: $(shell python --version 2>&1)"
	@echo "Docker Version: $(shell docker --version 2>&1)"
	@echo "Docker Compose Version: $(shell docker-compose --version 2>&1)"
	@echo ""
	@echo "=== SERVICES ==="
	@echo "Kafka UI: http://localhost:8080"
	@echo "Kafka Broker: localhost:9093"
	@echo "Zookeeper: localhost:2181"
	@echo "Schema Registry: localhost:8081" 