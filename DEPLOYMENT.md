# CoAgentics Deployment Guide

This guide covers deploying the CoAgentics application to Google Cloud Platform (GCP) using Docker containers and Cloud Run.

## 🏗️ Architecture Overview

The CoAgentics application consists of three main services:

- **Frontend** (Next.js): Port 3000 - React-based user interface
- **Backend** (FastAPI): Port 8002 - AI agent orchestration and APIs  
- **Fi MCP Server** (Go): Port 8080 - Financial data MCP server

## 📋 Prerequisites

### Required Software

1. **Docker & Docker Compose**
   ```bash
   # Install Docker Desktop (macOS/Windows)
   # Or install Docker Engine (Linux)
   
   # Verify installation
   docker --version
   docker-compose --version
   ```

2. **Google Cloud CLI**
   ```bash
   # Install gcloud CLI
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL
   
   # Verify installation
   gcloud --version
   ```

3. **Node.js & Python** (for local development)
   ```bash
   # Node.js 18+
   node --version
   
   # Python 3.11+
   python3 --version
   ```

### GCP Setup

1. **Create/Select GCP Project**
   ```bash
   # Set your project ID
   gcloud config set project YOUR_PROJECT_ID
   
   # Enable billing for the project (required for Cloud Run)
   ```

2. **Authenticate with GCP**
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

## 🚀 Deployment Options

### Option 1: Automated GCP Deployment (Recommended)

Use our automated deployment script for Cloud Run:

```bash
# Make scripts executable
chmod +x deployment/scripts/deploy.sh

# Deploy to GCP
./deployment/scripts/deploy.sh
```

This script will:
- Enable required GCP APIs
- Build and push Docker images to Container Registry
- Deploy all services to Cloud Run
- Provide service URLs

### Option 2: Manual GCP Deployment

1. **Enable Required APIs**
   ```bash
   gcloud services enable \
     cloudbuild.googleapis.com \
     run.googleapis.com \
     containerregistry.googleapis.com
   ```

2. **Deploy using Cloud Build**
   ```bash
   gcloud builds submit --config=deployment/gcp/cloudbuild.yaml .
   ```

3. **Get Service URLs**
   ```bash
   gcloud run services list --region=us-central1
   ```

### Option 3: Local Development with Docker

Use Docker Compose for local development:

```bash
# Create environment file
cp .env.example .env
# Edit .env with your configuration

# Start all services
./deployment/scripts/local-dev.sh start

# View logs
./deployment/scripts/local-dev.sh logs

# Stop services
./deployment/scripts/local-dev.sh stop
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# Firebase Configuration (for Frontend)
NEXT_PUBLIC_FIREBASE_API_KEY=your-firebase-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-firebase-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
NEXT_PUBLIC_FIREBASE_APP_ID=your-app-id

# API URLs (automatically set for GCP deployment)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_URL_V2=http://localhost:8002
```

### Firebase Setup

1. **Create Firebase Project**
   - Go to [Firebase Console](https://console.firebase.google.com)
   - Create new project or use existing one
   - Enable Authentication and Firestore

2. **Get Firebase Configuration**
   - Go to Project Settings > General
   - Scroll to "Your apps" section
   - Copy the config object

3. **Update Environment Variables**
   - Add Firebase config to your `.env` file
   - For GCP deployment, set these in Cloud Run console

## 🔧 Service Configuration

### Frontend (Next.js)

- **Port**: 3000
- **Memory**: 512Mi
- **CPU**: 1 vCPU
- **Key Features**: 
  - Standalone build for Docker
  - Firebase authentication
  - Chat interface and history

### Backend (FastAPI)

- **Port**: 8002
- **Memory**: 1Gi
- **CPU**: 2 vCPU
- **Key Features**:
  - AI agent orchestration
  - Vertex AI integration
  - Financial advisor agents

### Fi MCP Server (Go)

- **Port**: 8080
- **Memory**: 512Mi
- **CPU**: 1 vCPU
- **Key Features**:
  - Financial data access
  - MCP protocol implementation

## 📊 Monitoring & Logs

### View Logs in GCP

```bash
# Backend logs
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=coagentics-backend" --limit=50

# Frontend logs
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=coagentics-frontend" --limit=50

# MCP Server logs
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=fi-mcp-server" --limit=50
```

### Health Checks

All services include health check endpoints:
- Backend: `GET /health`
- Frontend: `GET /` (Next.js default)
- MCP Server: `GET /` (Go server root)

## 🛠️ Development Workflow

### Local Development

1. **Start services**
   ```bash
   ./deployment/scripts/local-dev.sh start
   ```

2. **Make changes** to your code

3. **Rebuild and restart**
   ```bash
   ./deployment/scripts/local-dev.sh build
   ./deployment/scripts/local-dev.sh restart
   ```

### Deployment

1. **Test locally** first
2. **Commit changes** to git
3. **Deploy to GCP**
   ```bash
   ./deployment/scripts/deploy.sh
   ```

## 🐛 Troubleshooting

### Common Issues

1. **Build Failures**
   ```bash
   # Check build logs
   gcloud builds list --limit=5
   gcloud builds log [BUILD_ID]
   ```

2. **Service Not Starting**
   ```bash
   # Check service logs
   gcloud logs read "resource.type=cloud_run_revision" --limit=10
   ```

3. **Environment Variables**
   ```bash
   # Update environment variables
   gcloud run services update SERVICE_NAME \
     --set-env-vars="KEY=VALUE" \
     --region=us-central1
   ```

4. **Docker Build Issues**
   ```bash
   # Clean Docker cache
   docker system prune -a
   
   # Rebuild without cache
   docker-compose build --no-cache
   ```

### Support Commands

```bash
# Check service status
gcloud run services list --region=us-central1

# Describe specific service
gcloud run services describe SERVICE_NAME --region=us-central1

# View recent deployments
gcloud run revisions list --service=SERVICE_NAME --region=us-central1

# Scale service
gcloud run services update SERVICE_NAME \
  --min-instances=1 \
  --max-instances=10 \
  --region=us-central1
```

## 💰 Cost Optimization

### Cloud Run Pricing Tips

1. **Set appropriate CPU/Memory** based on actual usage
2. **Use min-instances=0** for development (scales to zero)
3. **Monitor usage** in GCP Console
4. **Set up billing alerts**

### Resource Recommendations

- **Development**: Use provided defaults
- **Production**: Monitor and adjust based on traffic
- **High Traffic**: Consider using min-instances > 0

## 🔐 Security Considerations

1. **Service-to-Service Communication**
   - Services communicate over internal GCP networking
   - Use IAM for authentication between services

2. **Environment Variables**
   - Store secrets in Secret Manager (not environment variables)
   - Use IAM to control access

3. **Firebase Security**
   - Configure Firebase rules appropriately
   - Use authentication for protected routes

## 📈 Scaling

Cloud Run automatically scales based on:
- Incoming requests
- CPU/Memory usage
- Configured min/max instances

Adjust scaling settings:
```bash
gcloud run services update SERVICE_NAME \
  --min-instances=2 \
  --max-instances=50 \
  --concurrency=100 \
  --region=us-central1
```

---

## 🎯 Quick Start

For the fastest deployment:

1. **Set up GCP project and authentication**
2. **Run deployment script**:
   ```bash
   ./deployment/scripts/deploy.sh
   ```
3. **Update Firebase configuration** with deployed URLs
4. **Test the application**

That's it! Your CoAgentics application should be running on GCP Cloud Run. 🚀 