#!/bin/bash

# Setup script for Qdrant + ClickHouse + Vanna Text2SQL system

echo "Setting up Qdrant and ClickHouse for Vanna Text2SQL..."

# Function to check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "Docker is not installed. Please install Docker first."
        exit 1
    fi
}

# Function to check if docker-compose is available
check_docker_compose() {
    if command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker-compose"
    elif docker compose version &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker compose"
    else
        echo "Neither docker-compose nor docker compose is available."
        exit 1
    fi
}

# Create docker-compose.yml for services
create_docker_compose() {
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  qdrant:
    image: qdrant/qdrant:v1.7.3
    container_name: qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_storage:/qdrant/storage
    environment:
      - QDRANT__SERVICE__HTTP_PORT=6333
      - QDRANT__SERVICE__GRPC_PORT=6334
    restart: unless-stopped

  clickhouse:
    image: clickhouse/clickhouse-server:23.12
    container_name: clickhouse
    ports:
      - "8123:8123"
      - "9000:9000"
    volumes:
      - clickhouse_data:/var/lib/clickhouse
    environment:
      - CLICKHOUSE_DB=default
      - CLICKHOUSE_USER=default
      - CLICKHOUSE_PASSWORD=
    restart: unless-stopped

volumes:
  qdrant_storage:
  clickhouse_data:
EOF
    echo "✅ Created docker-compose.yml"
}

# Start services
start_services() {
    echo "Starting Qdrant and ClickHouse..."
    $DOCKER_COMPOSE_CMD up -d
    
    echo "Waiting for services to be ready..."
    sleep 10
    
    # Check if Qdrant is ready
    if curl -s http://localhost:6333/health > /dev/null; then
        echo "✅ Qdrant is running on http://localhost:6333"
    else
        echo "❌ Qdrant failed to start"
    fi
    
    # Check if ClickHouse is ready
    if curl -s http://localhost:8123/ping > /dev/null; then
        echo "✅ ClickHouse is running on http://localhost:8123"
    else
        echo "❌ ClickHouse failed to start"
    fi
}

# Install Python dependencies
install_dependencies() {
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
}

# Create sample data in ClickHouse
create_sample_data() {
    echo "Creating sample data in ClickHouse..."
    
    # Wait a bit more for ClickHouse to be fully ready
    sleep 5
    
    # Create sample tables and data
    curl -X POST 'http://localhost:8123' \
        -d "CREATE DATABASE IF NOT EXISTS vanna_demo"
    
    curl -X POST 'http://localhost:8123' \
        -d "CREATE TABLE IF NOT EXISTS vanna_demo.customers (
            id UInt32,
            name String,
            email String,
            country String,
            created_date Date
        ) ENGINE = MergeTree()
        ORDER BY id"
    
    curl -X POST 'http://localhost:8123' \
        -d "CREATE TABLE IF NOT EXISTS vanna_demo.orders (
            order_id UInt32,
            customer_id UInt32,
            product_name String,
            quantity UInt32,
            price Decimal(10,2),
            order_date Date
        ) ENGINE = MergeTree()
        ORDER BY order_id"
    
    # Insert sample data
    curl -X POST 'http://localhost:8123' \
        -d "INSERT INTO vanna_demo.customers VALUES 
            (1, 'John Doe', 'john@email.com', 'USA', '2023-01-15'),
            (2, 'Jane Smith', 'jane@email.com', 'Canada', '2023-02-20'),
            (3, 'Bob Johnson', 'bob@email.com', 'UK', '2023-03-10'),
            (4, 'Alice Brown', 'alice@email.com', 'Australia', '2023-04-05'),
            (5, 'Charlie Wilson', 'charlie@email.com', 'Germany', '2023-05-12')"
    
    curl -X POST 'http://localhost:8123' \
        -d "INSERT INTO vanna_demo.orders VALUES 
            (1, 1, 'Laptop', 1, 999.99, '2023-06-01'),
            (2, 1, 'Mouse', 2, 25.50, '2023-06-01'),
            (3, 2, 'Keyboard', 1, 75.00, '2023-06-15'),
            (4, 3, 'Monitor', 1, 299.99, '2023-07-01'),
            (5, 4, 'Tablet', 1, 399.99, '2023-07-15'),
            (6, 5, 'Phone', 1, 699.99, '2023-08-01'),
            (7, 2, 'Headphones', 1, 149.99, '2023-08-15'),
            (8, 3, 'Webcam', 1, 89.99, '2023-09-01')"
    
    echo "✅ Sample data created in ClickHouse"
}

# Copy environment file
setup_env() {
    if [ ! -f .env ]; then
        cp .env.example .env
        echo "✅ Created .env file from .env.example"
        echo "⚠️  Please update .env with your OpenAI API key and other settings"
    else
        echo "✅ .env file already exists"
    fi
}

# Main execution
main() {
    echo "🚀 Vanna Text2SQL Setup Script"
    echo "================================"
    
    check_docker
    check_docker_compose
    create_docker_compose
    start_services
    install_dependencies
    create_sample_data
    setup_env
    
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "Services running:"
    echo "  - Qdrant: http://localhost:6333"
    echo "  - ClickHouse: http://localhost:8123"
    echo ""
    echo "Next steps:"
    echo "  1. Update .env file with your OpenAI API key"
    echo "  2. Run the application: python main.py"
    echo "  3. Train the model using the /train/schema endpoint"
    echo "  4. Ask questions using the /ask endpoint"
    echo ""
    echo "Sample questions to try:"
    echo "  - 'How many customers do we have?'"
    echo "  - 'What are the total sales by country?'"
    echo "  - 'Show me the top 5 customers by order value'"
}

main "$@"