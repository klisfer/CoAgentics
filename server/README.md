# CoAgentics AI System

A sophisticated agentic AI system for financial intelligence, built with FastAPI and featuring multi-agent orchestration based on Google Cloud's Agentic AI Day architecture.

## 🏗️ Architecture Overview


CoAgentics implements a multi-agent architecture designed for financial AI applications:

### Core Components

- **Master Planner Agent**: Orchestrates and coordinates multiple specialized agents
- **Financial Assistant**: Provides general financial advice and market insights
- **Financial Advisor**: Advanced financial planning and advisory services
- **Portfolio Optimizer**: Specialized portfolio optimization and asset allocation
- **Research & Context Agent**: Market research and contextual information gathering

### Tools & Integrations

- **Web Search Tool**: Real-time market research and news gathering
- **Financial Calculator**: Comprehensive financial calculations and modeling
- **Vector Search**: Document and context retrieval (Vertex AI integration ready)
- **Cloud Storage**: Google Cloud Storage integration for data persistence

### Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM for database interactions
- **Pydantic**: Data validation using Python type annotations
- **JWT Authentication**: Secure user authentication and session management
- **CORS Support**: Cross-origin resource sharing for web integration

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Virtual environment (included in setup)

### Installation

1. **Navigate to the project directory:**
   ```bash
   cd CoAgentics
   ```

2. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate     # On Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the application:**
   ```bash
   python run.py
   ```

   Or using the FastAPI module directly:
   ```bash
   python -m app.main
   ```

## 📖 API Documentation

Once running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **API Info**: http://localhost:8000/api/info

## 🎯 Key Features

### Multi-Agent Orchestration
- Intelligent task routing and decomposition
- Coordinated responses from multiple specialized agents
- Context-aware agent selection and planning

### Financial Intelligence
- Real-time market analysis and research
- Portfolio optimization and asset allocation
- Retirement planning and investment advice
- Comprehensive financial calculations

### Extensible Architecture
- Modular agent system for easy expansion
- Tool integration framework
- Cloud-ready for Google Cloud Platform integration

## 📡 API Endpoints

### Chat Interface
- `POST /api/v1/chat/message` - Send messages to AI agents
- `GET /api/v1/chat/history` - Retrieve conversation history
- `GET /api/v1/chat/agents/status` - Get agent status information

### Financial Tools
- `POST /api/v1/tools/calculate` - Perform financial calculations
- `POST /api/v1/tools/web-search` - Search for market information
- `GET /api/v1/tools/calculate/types` - Get available calculation types

### System Endpoints
- `GET /health` - Comprehensive system health check
- `GET /agents/status` - Agent and tool status overview
- `POST /demo/quick-chat` - Demo chat without authentication

## 🧮 Financial Calculations

The system supports various financial calculations:

### Available Calculation Types
- **Compound Interest**: Calculate growth over time with compounding
- **Retirement Savings**: Project retirement savings and withdrawal rates
- **Loan Payments**: Calculate payments, interest, and payoff scenarios
- **Portfolio Analysis**: Expected returns, risk metrics, and optimization
- **Emergency Fund**: Calculate emergency fund requirements

### Example Usage

```bash
# Calculate compound interest
curl -X POST "http://localhost:8000/api/v1/tools/calculate/compound-interest" \
  -H "Content-Type: application/json" \
  -d '{
    "principal": 10000,
    "annual_rate": 7,
    "years": 10,
    "compounds_per_year": 12
  }'

# Get retirement savings projection
curl -X POST "http://localhost:8000/api/v1/tools/calculate/retirement" \
  -H "Content-Type: application/json" \
  -d '{
    "current_age": 30,
    "retirement_age": 65,
    "current_savings": 50000,
    "monthly_contribution": 1000,
    "annual_return": 8
  }'
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# Application Settings
ENVIRONMENT=development
DEBUG=True
APP_NAME="CoAgentics AI System"

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_PREFIX=/api/v1

# Database
DATABASE_URL=sqlite:///./coagentics.db

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google Cloud (Optional)
GOOGLE_CLOUD_PROJECT=your-project-id
VERTEX_AI_LOCATION=us-central1

# External APIs (Optional)
WEB_SEARCH_API_KEY=your-search-api-key
FINANCIAL_DATA_API_KEY=your-financial-api-key
```

## 🏗️ Project Structure

```
CoAgentics/
├── app/
│   ├── agents/                 # AI Agents
│   │   ├── base.py            # Base agent classes
│   │   ├── financial/         # Financial agents
│   │   └── planning/          # Planning and orchestration
│   ├── api/                   # API Layer
│   │   ├── routes/            # API route handlers
│   │   └── dependencies/      # API dependencies (auth, etc.)
│   ├── core/                  # Core functionality
│   │   ├── config.py          # Configuration management
│   │   └── database.py        # Database configuration
│   ├── models/                # Database models
│   ├── services/              # Business logic services
│   ├── tools/                 # Tool integrations
│   └── utils/                 # Utility functions
├── venv/                      # Virtual environment
├── requirements.txt           # Python dependencies
├── run.py                     # Application entry point
└── README.md                  # This file
```

## 🧪 Demo Mode

Try the system without authentication:

```bash
# Quick demo chat
curl -X POST "http://localhost:8000/demo/quick-chat?message=What%20is%20compound%20interest"
```

## 🔒 Authentication

The system supports JWT-based authentication. For production deployment:

1. Set a secure `SECRET_KEY` in environment variables
2. Implement user registration endpoints
3. Configure proper CORS settings
4. Set up HTTPS with SSL certificates

## 📊 Monitoring & Health

### Health Check
```bash
curl http://localhost:8000/health
```

### Agent Status
```bash
curl http://localhost:8000/agents/status
```

## 🌐 Production Deployment

For production deployment:

1. **Use a production ASGI server:**
   ```bash
   pip install gunicorn
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

2. **Database Setup:**
   - Use PostgreSQL or MySQL for production
   - Set up proper database migrations with Alembic
   - Configure connection pooling

3. **Security:**
   - Set secure environment variables
   - Configure proper CORS settings
   - Use HTTPS with SSL certificates
   - Implement rate limiting

4. **Cloud Integration:**
   - Deploy on Google Cloud Platform
   - Integrate with Vertex AI for enhanced capabilities
   - Use Google Cloud Storage for file storage
   - Configure monitoring and logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

[Add your license information here]

## 🆘 Support

For support and questions:
- Check the `/docs` endpoint for API documentation
- Review the logs for error details
- Ensure all dependencies are properly installed
- Verify environment configuration

---

**CoAgentics AI System** - Bringing sophisticated agentic AI to financial intelligence. 