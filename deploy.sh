#!/bin/bash

# ReachInbox Production Deployment Script
# This script automates the deployment process

set -e  # Exit on any error

echo "🚀 Starting ReachInbox Production Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons"
   exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from template..."
    cp .env.example .env
    print_warning "Please edit .env file with your actual credentials before continuing"
    exit 1
fi

print_status "Environment file found ✓"

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p ssl
mkdir -p reply_vector_db

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_status "Docker and Docker Compose found ✓"

# Stop any existing containers
print_status "Stopping existing containers..."
docker-compose -f docker-compose.production.yml down || true

# Pull latest images
print_status "Pulling latest Docker images..."
docker-compose -f docker-compose.production.yml pull

# Build application images
print_status "Building application images..."
docker-compose -f docker-compose.production.yml build

# Start services
print_status "Starting services..."
docker-compose -f docker-compose.production.yml up -d

# Wait for services to be ready
print_status "Waiting for services to start..."
sleep 30

# Check service health
print_status "Checking service health..."

# Check Elasticsearch
if curl -s http://localhost:9200/_cluster/health > /dev/null; then
    print_status "Elasticsearch is running ✓"
else
    print_error "Elasticsearch is not responding"
fi

# Check main application
if curl -s http://localhost:4000/health > /dev/null; then
    print_status "Main application is running ✓"
else
    print_warning "Main application might still be starting..."
fi

# Check Redis
if docker exec reachinbox-redis redis-cli ping > /dev/null 2>&1; then
    print_status "Redis is running ✓"
else
    print_error "Redis is not responding"
fi

# Show running containers
print_status "Running containers:"
docker-compose -f docker-compose.production.yml ps

# Show logs command
print_status "View logs with: docker-compose -f docker-compose.production.yml logs -f"

# Final status
print_status "🎉 Deployment complete!"
print_status "Application available at: http://localhost"
print_status "Kibana available at: http://localhost:5601"

echo ""
echo "📋 Quick Commands:"
echo "  View logs: docker-compose -f docker-compose.production.yml logs -f"
echo "  Stop services: docker-compose -f docker-compose.production.yml down"
echo "  Restart services: docker-compose -f docker-compose.production.yml restart"
echo "  Update application: ./deploy.sh"
