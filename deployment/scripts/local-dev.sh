#!/bin/bash

# CoAgentics Local Development Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install it first."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install it first."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Please create one based on .env.example"
    echo "Required environment variables:"
    echo "  - GOOGLE_CLOUD_PROJECT"
    echo "  - GOOGLE_APPLICATION_CREDENTIALS"
    echo "  - NEXT_PUBLIC_FIREBASE_* (Firebase config)"
    exit 1
fi

print_status "Starting CoAgentics local development environment..."

# Parse command line arguments
case "${1:-start}" in
    "start")
        print_status "Building and starting all services..."
        docker-compose up --build -d
        
        print_status "Waiting for services to be ready..."
        sleep 10
        
        # Check service health
        print_status "Checking service health..."
        
        # Check MCP Server
        if curl -f http://localhost:8080 >/dev/null 2>&1; then
            print_success "Fi MCP Server is running on http://localhost:8080"
        else
            print_warning "Fi MCP Server may not be ready yet"
        fi
        
        # Check Backend
        if curl -f http://localhost:8002/health >/dev/null 2>&1; then
            print_success "Backend is running on http://localhost:8002"
        else
            print_warning "Backend may not be ready yet"
        fi
        
        # Check Frontend
        if curl -f http://localhost:3000 >/dev/null 2>&1; then
            print_success "Frontend is running on http://localhost:3000"
        else
            print_warning "Frontend may not be ready yet"
        fi
        
        print_success "Development environment is ready!"
        echo ""
        echo "🌟 Service URLs:"
        echo "   Frontend:   http://localhost:3000"
        echo "   Backend:    http://localhost:8002"
        echo "   MCP Server: http://localhost:8080"
        echo ""
        echo "📋 Useful commands:"
        echo "   View logs:    docker-compose logs -f"
        echo "   Stop:         docker-compose down"
        echo "   Restart:      docker-compose restart"
        ;;
    
    "stop")
        print_status "Stopping all services..."
        docker-compose down
        print_success "All services stopped"
        ;;
    
    "restart")
        print_status "Restarting all services..."
        docker-compose restart
        print_success "All services restarted"
        ;;
    
    "logs")
        print_status "Showing logs..."
        docker-compose logs -f
        ;;
    
    "build")
        print_status "Rebuilding all services..."
        docker-compose build --no-cache
        print_success "All services rebuilt"
        ;;
    
    "clean")
        print_status "Cleaning up containers and images..."
        docker-compose down -v --rmi all
        docker system prune -f
        print_success "Cleanup completed"
        ;;
    
    *)
        echo "Usage: $0 {start|stop|restart|logs|build|clean}"
        echo ""
        echo "Commands:"
        echo "  start   - Build and start all services (default)"
        echo "  stop    - Stop all services"
        echo "  restart - Restart all services"
        echo "  logs    - Show logs from all services"
        echo "  build   - Rebuild all services"
        echo "  clean   - Clean up containers and images"
        exit 1
        ;;
esac 