# Multi-Touch Attribution Analytics Platform

A comprehensive, enterprise-grade multi-touch attribution analytics platform built with modern Python architecture, featuring FastAPI backend, Streamlit frontend, and advanced attribution modeling capabilities.

## 🚀 Features

### Core Attribution Models
- **First-Touch Attribution**: 100% credit to the first touchpoint
- **Last-Touch Attribution**: 100% credit to the last touchpoint
- **Linear Attribution**: Equal credit distribution across all touchpoints
- **Time-Decay Attribution**: Exponential decay based on time to conversion
- **U-Shaped Attribution**: Higher weight for first and last touches
- **W-Shaped Attribution**: Credit to first touch, lead creation, and opportunity creation
- **Data-Driven Attribution**: Machine learning-based attribution weighting

### Platform Capabilities
- **Real-time Analytics**: Live attribution calculation and reporting
- **Customer Journey Mapping**: Comprehensive touchpoint visualization
- **Channel Performance Analysis**: Multi-channel ROI and effectiveness metrics
- **Data Ingestion**: Support for multiple data sources and formats
- **Advanced Visualization**: Interactive dashboards and reports
- **API-First Architecture**: RESTful API for system integration
- **Scalable Processing**: Celery-based background task processing
- **Enterprise Security**: Authentication, authorization, and audit logging

## 🏗️ Architecture

### Backend (FastAPI)
- **Modern Python 3.11+** with type hints and async support
- **FastAPI** for high-performance API development
- **SQLAlchemy** with PostgreSQL for data persistence
- **Redis** for caching and session management
- **Celery** for asynchronous task processing
- **Pydantic** for data validation and serialization
- **Structured Logging** with comprehensive monitoring

### Frontend (Streamlit)
- **Streamlit** for rapid UI development
- **Plotly** for interactive visualizations
- **Pandas** for data manipulation and analysis
- **Modern responsive design** with custom CSS
- **Real-time API integration** with the backend

### Infrastructure
- **Docker** containerization for all services
- **PostgreSQL** for primary data storage
- **Redis** for caching and message queuing
- **Nginx** for reverse proxy and load balancing
- **Prometheus & Grafana** for monitoring and alerting
- **GitHub Actions** for CI/CD automation

## 📋 Prerequisites

- **Python 3.11+**
- **Docker & Docker Compose**
- **Git**
- **8GB+ RAM** (recommended for full stack)

## ⚡ Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/multi-touch-attribution.git
cd multi-touch-attribution
```

### 2. Environment Setup
```bash
# Create environment file
cp .env.example .env

# Edit environment variables
nano .env
```

### 3. Start with Docker Compose
```bash
# Start all services
docker-compose up -d

# Check service health
docker-compose ps
```

### 4. Access the Applications
- **Frontend (Streamlit)**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Monitoring (Grafana)**: http://localhost:3000
- **Task Monitor (Flower)**: http://localhost:5555

### 5. Initial Data Setup
```bash
# Load sample data
docker-compose exec backend python scripts/load_sample_data.py

# Run initial attribution calculations
docker-compose exec backend python scripts/calculate_attribution.py
```

## 🔧 Development Setup

### Local Development
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Start services locally
# Terminal 1: Database & Redis
docker-compose up postgres redis

# Terminal 2: Backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 3: Frontend
cd frontend
streamlit run main.py

# Terminal 4: Celery Worker
celery -A backend.app.core.celery worker --loglevel=info
```

### Environment Variables
```bash
# Database
DB_URL=postgresql://user:password@localhost:5432/attribution_db

# Redis
REDIS_URL=redis://localhost:6379/0

# API Settings
API_SECRET_KEY=your-secret-key-here
API_DEBUG=false

# Attribution Settings
ATTRIBUTION_DEFAULT_MODELS=first_touch,last_touch,linear,time_decay
ATTRIBUTION_LOOKBACK_WINDOW_DAYS=90
```

## 📊 Usage Examples

### API Usage

#### Calculate Attribution
```python
import httpx

# Calculate attribution for a customer journey
response = httpx.post(
    "http://localhost:8000/api/v1/attribution/calculate",
    json={
        "customer_id": "customer_123",
        "touchpoints": [
            {
                "id": "tp_1",
                "timestamp": "2024-01-01T10:00:00Z",
                "channel": "organic_search",
                "cost": 0.0
            },
            {
                "id": "tp_2", 
                "timestamp": "2024-01-02T14:00:00Z",
                "channel": "paid_search",
                "cost": 5.50
            }
        ],
        "conversion": {
            "timestamp": "2024-01-03T16:00:00Z",
            "value": 100.0
        },
        "models": ["linear", "time_decay", "u_shaped"]
    }
)

attribution_results = response.json()
```

#### Retrieve Channel Performance
```python
# Get channel performance metrics
response = httpx.get(
    "http://localhost:8000/api/v1/analytics/channel-performance",
    params={
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
        "attribution_model": "linear"
    }
)

performance_data = response.json()
```

### Python SDK Usage
```python
from backend.app.services.attribution_models import (
    AttributionModelFactory,
    compare_attribution_models
)

# Create attribution model
model = AttributionModelFactory.create_model("time_decay", half_life_days=7)

# Calculate attribution
touchpoints = [
    {
        'id': 'tp_1',
        'timestamp': datetime(2024, 1, 1),
        'channel_id': 'organic_search'
    },
    # ... more touchpoints
]

attribution = model.calculate_attribution(touchpoints, conversion_value=100.0)

# Compare multiple models
comparison_df = compare_attribution_models(
    touchpoints, 
    conversion_value=100.0,
    models=['first_touch', 'last_touch', 'linear']
)
```

## 🧪 Testing

### Run All Tests
```bash
# Unit tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=backend --cov=frontend --cov-report=html

# Integration tests
pytest tests/integration/ -v

# Performance tests
pytest tests/performance/ -v -m slow
```

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: API and database integration
- **Performance Tests**: Load and stress testing
- **Security Tests**: Vulnerability scanning

## 📈 Monitoring & Observability

### Metrics & Monitoring
- **Application Metrics**: Request rates, response times, error rates
- **Business Metrics**: Attribution calculations, conversion rates, channel performance
- **System Metrics**: CPU, memory, disk usage, database performance
- **Custom Dashboards**: Grafana dashboards for visualization

### Logging
- **Structured Logging**: JSON-formatted logs for easy parsing
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log Aggregation**: Centralized logging with log rotation
- **Performance Logging**: Request timing and resource usage

### Health Checks
```bash
# Check API health
curl http://localhost:8000/health

# Check all services
docker-compose ps
```

## 🔒 Security

### Authentication & Authorization
- **JWT-based authentication** for API access
- **Role-based access control** (RBAC)
- **API key management** for external integrations
- **Session management** with Redis

### Security Features
- **Input validation** with Pydantic models
- **SQL injection prevention** with parameterized queries
- **Rate limiting** for API endpoints
- **HTTPS enforcement** in production
- **Security headers** and CORS configuration

### Security Scanning
```bash
# Run security scans
bandit -r backend/
safety check
semgrep --config=auto backend/
```

## 🚀 Deployment

### Production Deployment
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

### Cloud Deployment

#### AWS ECS
```bash
# Deploy to AWS ECS using the provided GitHub Actions workflow
# Configure AWS credentials and run the deployment action
```

#### Kubernetes
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n attribution
```

### Environment-Specific Configurations
- **Development**: Local development with debugging enabled
- **Staging**: Production-like environment for testing
- **Production**: Optimized for performance and security

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

### Key Endpoints

#### Attribution
- `POST /api/v1/attribution/calculate` - Calculate attribution
- `GET /api/v1/attribution/models` - List available models
- `GET /api/v1/attribution/results/{customer_id}` - Get attribution results

#### Analytics
- `GET /api/v1/analytics/channel-performance` - Channel performance metrics
- `GET /api/v1/analytics/customer-journey/{customer_id}` - Customer journey
- `GET /api/v1/analytics/conversion-funnel` - Conversion funnel analysis

#### Data Management
- `POST /api/v1/data/touchpoints` - Bulk import touchpoints
- `POST /api/v1/data/conversions` - Bulk import conversions
- `GET /api/v1/data/status` - Data processing status

## 🤝 Contributing

### Development Workflow
1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/new-feature`
3. **Make changes and add tests**
4. **Run tests**: `pytest tests/`
5. **Run linting**: `flake8 backend/ frontend/`
6. **Format code**: `black backend/ frontend/`
7. **Commit changes**: `git commit -m "Add new feature"`
8. **Push to branch**: `git push origin feature/new-feature`
9. **Create Pull Request**

### Code Standards
- **Python**: Follow PEP 8 style guide
- **Type Hints**: Use type annotations throughout
- **Documentation**: Comprehensive docstrings for all functions
- **Testing**: Minimum 80% code coverage
- **Logging**: Structured logging for all operations

### Pull Request Requirements
- [ ] All tests pass
- [ ] Code coverage maintained
- [ ] Documentation updated
- [ ] Security scan passes
- [ ] Performance benchmarks met

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help
- **GitHub Issues**: Report bugs and request features
- **Documentation**: Comprehensive guides and API reference
- **Community**: Join our discussion forums
- **Enterprise Support**: Contact us for commercial support

### Common Issues
- **Database Connection**: Ensure PostgreSQL is running and accessible
- **Memory Issues**: Increase Docker memory allocation for large datasets
- **Performance**: Check Redis connection and enable caching
- **Authentication**: Verify JWT token configuration

### Resources
- [Architecture Documentation](docs/architecture.md)
- [API Reference](docs/api.md)
- [Deployment Guide](docs/deployment.md)
- [Performance Tuning](docs/performance.md)
- [Troubleshooting Guide](docs/troubleshooting.md)

---

**Multi-Touch Attribution Platform** - Enterprise-grade attribution analytics for modern marketing teams.
