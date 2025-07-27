#!/bin/bash

# CoAgentics GCP Deployment Script
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

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    print_error "gcloud CLI is not installed. Please install it first."
    exit 1
fi

# Note: Docker is not required locally for GCP Cloud Build deployment
# Docker builds happen in the cloud

# Get project ID
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    print_error "No GCP project set. Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

print_status "Deploying CoAgentics to GCP Project: $PROJECT_ID"

# Enable required APIs
print_status "Enabling required GCP APIs..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    containerregistry.googleapis.com \
    artifactregistry.googleapis.com

# Note: Docker authentication not needed for Cloud Build deployment

# Set build timeout
export CLOUDBUILD_TIMEOUT=1200s

# Deploy using Cloud Build
print_status "Starting Cloud Build deployment..."
gcloud builds submit --config=deployment/gcp/cloudbuild.yaml .

# Get service URLs
print_status "Getting service URLs..."
MCP_URL=$(gcloud run services describe fi-mcp-server --region=us-central1 --format='value(status.url)')
BACKEND_URL=$(gcloud run services describe coagentics-backend --region=us-central1 --format='value(status.url)')
FRONTEND_URL=$(gcloud run services describe coagentics-frontend --region=us-central1 --format='value(status.url)')

print_success "Deployment completed successfully!"
echo ""
echo "🌟 Service URLs:"
echo "   Frontend:   $FRONTEND_URL"
echo "   Backend:    $BACKEND_URL"
echo "   MCP Server: $MCP_URL"
echo ""
echo "📋 Next steps:"
echo "   1. Update your Firebase configuration with the frontend URL"
echo "   2. Update environment variables in Cloud Run console if needed"
echo "   3. Test the application at: $FRONTEND_URL"

# Optional: Open the frontend URL
read -p "Open frontend URL in browser? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v open &> /dev/null; then
        open "$FRONTEND_URL"
    elif command -v xdg-open &> /dev/null; then
        xdg-open "$FRONTEND_URL"
    else
        print_warning "Cannot open browser automatically. Please visit: $FRONTEND_URL"
    fi
fi 