# CoAgentics - AI-Powered Financial Advisory Platform

> 🤖 An intelligent financial advisory system that combines AI agents, voice interaction, and personalized financial planning to provide comprehensive financial guidance.

## 📖 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
- [Production Deployment](#production-deployment)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)

## 🌟 Overview

CoAgentics is a modern financial advisory platform that leverages cutting-edge AI technology to provide personalized financial advice. The platform features multiple specialized AI agents, voice interaction capabilities, and real-time financial tools to help users make informed financial decisions.

### Key Capabilities

- **🎯 Multi-Agent AI System**: Specialized agents for different financial domains (investment, tax, insurance, etc.)
- **🎤 Voice Interaction**: Speak to your financial advisor using advanced voice recognition
- **📊 Real-time Financial Data**: Live market data, transaction tracking, and portfolio analysis
- **👤 Personalized Advice**: Tailored recommendations based on user profiles and financial goals
- **🔐 Secure Authentication**: Firebase-powered authentication with user profile management
- **📱 Responsive Design**: Works seamlessly across desktop and mobile devices

## 🏗️ Architecture

CoAgentics follows a microservices architecture with three main components:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js       │    │   FastAPI       │    │   Go MCP        │
│   Frontend      │◄──►│   Backend       │◄──►│   Server        │
│   (Port 3000)   │    │   (Port 8002)   │    │   (Port 8080)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Firebase      │    │   Google Cloud  │    │   Financial     │
│   Auth & DB     │    │   AI Platform   │    │   Data APIs     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Component Details

- **Frontend (Next.js)**: Modern React-based UI with TypeScript, Tailwind CSS, and real-time chat interface
- **Backend (FastAPI)**: Python-based API server with AI agent orchestration and voice processing
- **MCP Server (Go)**: Model Context Protocol server for financial data integration
- **AI Platform**: Google Vertex AI for agent management and Gemini 2.5 Pro for voice/text processing

## ✨ Features

### 🤖 AI Financial Agents
- **Master Planner**: Orchestrates conversations and routes to appropriate specialists
- **Investment Advisor**: Portfolio analysis, stock recommendations, market insights
- **Tax Consultant**: Tax planning, optimization strategies, compliance guidance
- **Insurance Advisor**: Coverage analysis, policy recommendations, risk assessment
- **Financial Assistant**: General financial queries, budgeting, expense tracking

### 🎤 Voice Interaction
- **Hold-to-Talk**: Natural voice recording with visual feedback
- **Real-time Transcription**: Powered by Gemini 2.5 Pro for accurate speech-to-text
- **Multi-language Support**: English (US/India) with Hindi support
- **Audio Format Support**: WebM, MP3, WAV, and OGG formats

### 📊 Financial Tools
- **Live Market Data**: Real-time stock prices, crypto rates, market indices
- **Portfolio Tracking**: Investment performance, asset allocation, P&L analysis
- **Transaction History**: Bank transactions, mutual fund investments, EPF details
- **Credit Monitoring**: Credit report analysis and score tracking

### 🔐 Security & Privacy
- **Firebase Authentication**: Secure user registration and login
- **Session Management**: Persistent chat sessions with context retention
- **Data Encryption**: End-to-end encryption for sensitive financial data
- **GDPR Compliance**: Privacy-first approach to data handling

## 🛠️ Tech Stack

### Frontend
- **Next.js 15**: React framework with App Router
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Firebase SDK**: Authentication and database
- **Axios**: HTTP client for API calls
- **Framer Motion**: Smooth animations

### Backend
- **FastAPI**: Modern Python web framework
- **Google ADK**: Agent Development Kit for AI orchestration
- **Google Vertex AI**: AI platform for agent management
- **Google Generative AI**: Gemini models for text and voice processing
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server

### MCP Server
- **Go**: High-performance language for financial data processing
- **Gorilla Mux**: HTTP router and URL matcher
- **JSON APIs**: RESTful endpoints for financial data

### Infrastructure
- **Google Cloud Platform**: Cloud hosting and AI services
- **Firebase**: Authentication and Firestore database
- **Docker**: Containerization for deployment
- **Docker Compose**: Multi-service orchestration

## 📋 Prerequisites

Before setting up CoAgentics, ensure you have the following installed:

### Required Software
- **Node.js** (v18 or higher) - [Download](https://nodejs.org/)
- **Python** (v3.8 or higher) - [Download](https://python.org/)
- **Go** (v1.19 or higher) - [Download](https://golang.org/)
- **Git** - [Download](https://git-scm.com/)

### Required Accounts & Services
- **Google Cloud Platform Account** - [Sign up](https://cloud.google.com/)
- **Firebase Project** - [Create project](https://console.firebase.google.com/)
- **Google Cloud Project** with the following APIs enabled:
  - Vertex AI API
  - Generative AI API
  - Cloud Speech-to-Text API (optional)

### Development Tools (Recommended)
- **VS Code** with extensions:
  - Python
  - TypeScript
  - Go
  - Docker
  - Firebase

## 🚀 Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/CoAgentics.git
cd CoAgentics
```

### 2. Environment Configuration

Copy the environment template and configure your settings:

```bash
cp env.template .env
```

Edit `.env` with your actual values:

```bash
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# Firebase Configuration
NEXT_PUBLIC_FIREBASE_API_KEY=your-firebase-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-firebase-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
NEXT_PUBLIC_FIREBASE_APP_ID=your-app-id

# Local Development URLs
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_URL_V2=http://localhost:8002
```

### 3. Google Cloud Setup

#### Create Service Account
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to **IAM & Admin > Service Accounts**
4. Click **Create Service Account**
5. Give it these roles:
   - Vertex AI User
   - Generative AI User
   - Cloud Speech Client (optional)
6. Download the JSON key file
7. Update `GOOGLE_APPLICATION_CREDENTIALS` in `.env`

#### Enable Required APIs
```bash
gcloud services enable aiplatform.googleapis.com
gcloud services enable generativelanguage.googleapis.com
```

### 4. Firebase Setup

#### Create Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or use existing
3. Enable **Authentication** and **Firestore Database**
4. In **Project Settings**, copy the config values to your `.env`

#### Authentication Setup
1. In Firebase Console, go to **Authentication > Sign-in method**
2. Enable **Google** sign-in provider
3. Add your domain to authorized domains

### 5. Backend Setup

```bash
# Navigate to server directory
cd server

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file in server/app directory
cd app
cat > .env << 'EOF'
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-central1
# Note: GOOGLE_APPLICATION_CREDENTIALS will auto-detect from ~/.config/gcloud/
EOF

# Start the backend server
cd ..
uvicorn app.main2:app --reload --host 0.0.0.0 --port 8002
```

### 6. MCP Server Setup

```bash
# Navigate to MCP server directory
cd fi-mcp-server

# Install Go dependencies
go mod tidy

# Build and run the MCP server
go run main.go
```

The MCP server will start on port 8080.

### 7. Frontend Setup

```bash
# Navigate to client directory
cd client

# Install dependencies
npm install

# Create local environment file
cat > .env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_URL_V2=http://localhost:8002
NEXT_PUBLIC_FIREBASE_API_KEY=your-firebase-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-firebase-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
NEXT_PUBLIC_FIREBASE_APP_ID=your-app-id
EOF

# Start the development server
npm run dev
```

### 8. Verify Setup

1. **Frontend**: Open [http://localhost:3000](http://localhost:3000)
2. **Backend**: Check [http://localhost:8002/health](http://localhost:8002/health)
3. **MCP Server**: Check [http://localhost:8080/](http://localhost:8080/)

### 9. Test the Application

1. **Sign Up/Login**: Create an account using Google Sign-In
2. **Text Chat**: Send a message to test the AI agents
3. **Voice Chat**: Click the microphone button and test voice interaction
4. **Financial Tools**: Try asking about investments, taxes, or insurance

## 🚀 Production Deployment

### Option 1: Docker Compose (Recommended)

#### 1. Prepare Environment
```bash
# Copy and configure environment for production
cp env.template .env
# Edit .env with production values
```

#### 2. Update Production URLs
```bash
# In .env file
NEXT_PUBLIC_API_URL=https://your-backend-service-url
NEXT_PUBLIC_API_URL_V2=https://your-backend-v2-service-url
```

#### 3. Deploy with Docker Compose
```bash
# Build and start all services
docker-compose up -d --build

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

#### 4. Health Checks
- Frontend: `http://your-domain:3000`
- Backend: `http://your-domain:8002/health`
- MCP Server: `http://your-domain:8080/`

### Option 2: Google Cloud Run

#### 1. Setup Google Cloud CLI
```bash
# Install Google Cloud CLI
# Configure authentication
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

#### 2. Deploy Backend
```bash
cd server

# Build and deploy
gcloud run deploy coagentics-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --port 8002 \
  --set-env-vars GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID,GOOGLE_CLOUD_LOCATION=us-central1
```

#### 3. Deploy MCP Server
```bash
cd fi-mcp-server

# Build and deploy
gcloud run deploy coagentics-mcp \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --port 8080
```

#### 4. Deploy Frontend
```bash
cd client

# Update environment variables with Cloud Run URLs
# Build and deploy
gcloud run deploy coagentics-frontend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --port 3000 \
  --set-env-vars NODE_ENV=production,NEXT_PUBLIC_API_URL=https://your-backend-url,NEXT_PUBLIC_API_URL_V2=https://your-backend-url
```

### Option 3: Kubernetes

Refer to `deployment/kubernetes/` directory for Kubernetes manifests and deployment instructions.

## 📚 API Documentation

### Authentication Endpoints
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /auth/profile` - Get user profile

### Chat Endpoints
- `POST /chat` - Send text message to AI agents
- `POST /api/v2/chat` - Send text or voice message (unified endpoint)
- `GET /system/status` - Get system and agent status

### Financial Data Endpoints
- `GET /api/financial/portfolio` - Get portfolio data
- `GET /api/financial/transactions` - Get transaction history
- `GET /api/financial/market-data` - Get live market data

### Health Check
- `GET /health` - Service health status
- `GET /system/agents` - Get available AI agents

For detailed API documentation, visit `/docs` when running the backend server.

## 📁 Project Structure

```
CoAgentics/
├── client/                          # Next.js Frontend
│   ├── src/
│   │   ├── app/                     # App Router pages
│   │   ├── components/              # React components
│   │   │   ├── chat/               # Chat interface components
│   │   │   ├── calculators/        # Financial calculator tools
│   │   │   └── layout/             # Layout components
│   │   ├── hooks/                  # Custom React hooks
│   │   ├── lib/                    # Utilities and API clients
│   │   └── services/               # Firebase and other services
│   ├── public/                     # Static assets
│   └── package.json               # Frontend dependencies
│
├── server/                         # FastAPI Backend
│   ├── app/
│   │   ├── agents/                # AI agent implementations
│   │   ├── api/                   # API route handlers
│   │   ├── core/                  # Core configurations
│   │   ├── models/                # Pydantic models
│   │   ├── services/              # Business logic services
│   │   ├── tools/                 # AI agent tools
│   │   ├── utils/                 # Utility functions
│   │   └── main2.py              # FastAPI application entry point
│   └── requirements.txt          # Python dependencies
│
├── fi-mcp-server/                 # Go MCP Server
│   ├── pkg/                      # Go packages
│   ├── middlewares/              # HTTP middlewares
│   ├── static/                   # Static data files
│   ├── main.go                   # Go application entry point
│   └── go.mod                    # Go dependencies
│
├── deployment/                    # Deployment configurations
│   ├── docker/                   # Docker files
│   ├── kubernetes/               # K8s manifests
│   └── gcp/                      # Google Cloud deployment scripts
│
├── .vscode/                      # VS Code configuration
├── docker-compose.yml           # Multi-service deployment
├── env.template                 # Environment configuration template
└── README.md                    # Project documentation
```

## 🤝 Contributing

We welcome contributions to CoAgentics! Please follow these guidelines:

### Development Workflow
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `npm test` (frontend) and `pytest` (backend)
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Code Standards
- **Frontend**: Follow ESLint rules, use TypeScript, write component tests
- **Backend**: Follow PEP 8, type hints required, write unit tests
- **Go**: Follow Go conventions, use gofmt, write table-driven tests

### Commit Guidelines
- Use conventional commits: `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`
- Keep commits focused and atomic
- Write clear commit messages

## 🔧 Troubleshooting

### Common Issues

#### 1. Authentication Errors
**Problem**: `Invalid JWT Signature` or `Credentials not found`

**Solution**:
```bash
# Check if Google Cloud credentials are set
echo $GOOGLE_APPLICATION_CREDENTIALS

# Re-authenticate with gcloud
gcloud auth application-default login

# Verify the service account file exists and is readable
ls -la $GOOGLE_APPLICATION_CREDENTIALS
```

#### 2. Voice Chat Not Working
**Problem**: Voice messages show "Voice message" instead of transcription

**Solutions**:
- Check if `google-generativeai` is installed: `pip show google-generativeai`
- Verify Vertex AI API is enabled in Google Cloud Console
- Check browser microphone permissions
- Ensure audio format is supported (WebM, MP3, WAV)

#### 3. Frontend Build Errors
**Problem**: Next.js build fails with module errors

**Solutions**:
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check Node.js version
node --version  # Should be v18+

# Update dependencies
npm update
```

#### 4. Backend Connection Issues
**Problem**: `Connection refused` or `500 Internal Server Error`

**Solutions**:
```bash
# Check if services are running
ps aux | grep python  # Backend
ps aux | grep go       # MCP server

# Check ports are not in use
lsof -i :8002  # Backend
lsof -i :8080  # MCP server

# Restart services
pkill -f python
uvicorn app.main2:app --reload --host 0.0.0.0 --port 8002
```

#### 5. Firebase Connection Issues
**Problem**: Authentication or Firestore errors

**Solutions**:
- Check Firebase project settings match `.env` values
- Verify Firebase rules allow your operations
- Check if billing is enabled for Firestore
- Ensure your domain is in authorized domains list

### Getting Help

1. **Check Logs**: Always check console logs and server logs first
2. **Documentation**: Refer to specific component documentation
3. **Issues**: Create a GitHub issue with detailed error information
4. **Discord**: Join our community Discord for real-time help
5. **Email**: Contact support at support@coagentics.com

### Performance Optimization

#### Frontend
- Use Next.js Image optimization
- Implement proper caching strategies
- Minimize bundle size with tree shaking
- Use React.memo for expensive components

#### Backend
- Enable FastAPI response caching
- Use connection pooling for database
- Implement request rate limiting
- Monitor and optimize AI agent response times

#### Infrastructure
- Use CDN for static assets
- Implement load balancing
- Set up proper monitoring and alerting
- Use horizontal pod autoscaling in Kubernetes

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Cloud Platform** for AI and infrastructure services
- **Firebase** for authentication and database
- **Vercel** for Next.js framework and deployment platform
- **FastAPI** community for the excellent Python framework
- **Go community** for the robust programming language

---

<div align="center">

**Built with ❤️ by the CoAgentics Team**


</div> 