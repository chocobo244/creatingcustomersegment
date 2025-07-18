# 🎯 B2B Marketing Attribution Platform

A comprehensive, enterprise-grade B2B marketing attribution platform designed specifically for complex sales cycles, account-based marketing, and sophisticated B2B attribution models.

## 🌟 Overview

This platform provides advanced B2B marketing attribution analysis with specialized features for:

- **Complex B2B Sales Cycles** (3-18 months)
- **Lead Quality Scoring** and demographic analysis
- **Account-Based Marketing** attribution
- **Sales-Marketing Alignment** tracking
- **Pipeline Velocity** optimization
- **Multi-touchpoint Attribution** across buying committees

## 🚀 Key Features

### 🎯 B2B Marketing Attribution Engine

Our sophisticated attribution engine is specifically designed for B2B marketing workflows:

#### **Multi-Factor Attribution Analysis**
- **Time-Weighted Attribution**: Accounts for long B2B sales cycles with gentler decay curves
- **Lead Quality Impact**: Weights touchpoints by lead scoring and demographic fit  
- **Account-Based Attribution**: Considers buying committee complexity and deal size
- **Stage Progression**: Tracks touchpoint influence on funnel advancement
- **Pipeline Velocity**: Measures impact on sales cycle acceleration

#### **B2B-Specific Touchpoint Types**
- Demo Requests (Weight: 1.5x)
- Sales Calls (Weight: 1.4x)
- Webinar Attendance (Weight: 1.2x)
- Content Downloads (Weight: 1.1x)
- Trade Shows (Weight: 1.3x)
- Referrals (Weight: 1.6x)
- And more...

#### **Lead Quality Tiers**
- **A-Tier Leads**: 1.5x attribution multiplier
- **B-Tier Leads**: 1.2x attribution multiplier
- **C-Tier Leads**: 1.0x attribution multiplier
- **D-Tier Leads**: 0.7x attribution multiplier

#### **Deal Size Support**
- **Enterprise**: 270-day avg sales cycle, complex attribution
- **Mid-Market**: 150-day avg sales cycle, moderate complexity
- **SMB**: 60-day avg sales cycle, simplified attribution

### 📊 Advanced Analytics

#### **Sales-Marketing Alignment Analysis**
- Attribution split between sales and marketing touchpoints
- Joint touchpoint identification and analysis
- Alignment score calculation (0-100)
- Letter grade assessment (A+ to F)
- Actionable recommendations for improvement

#### **Channel Performance Insights**
- ROI analysis by marketing channel
- Cost efficiency metrics
- Touchpoint volume analysis
- Optimization recommendations

#### **Pipeline Velocity Tracking**
- Sales cycle acceleration analysis
- Touchpoint impact on deal velocity
- Velocity benchmarks by deal size
- Predictive cycle length modeling

## 🏗️ Architecture

### Backend (FastAPI)
```
backend/
├── app/
│   ├── api/routes/attribution.py          # B2B attribution API endpoints
│   ├── services/
│   │   ├── b2b_attribution_engine.py      # Core B2B attribution engine
│   │   └── attribution_service.py         # Service layer integration
│   ├── models/                            # Database models
│   └── utils/                            # Utilities and logging
├── tests/
│   └── test_b2b_attribution_engine.py    # Comprehensive B2B tests
└── config/settings.py                    # Configuration management
```

### Frontend (Streamlit)
```
frontend/
├── pages/
│   └── b2b_attribution.py               # B2B attribution dashboard
├── utils/
│   ├── api_client.py                     # API integration
│   └── visualization.py                 # Chart components
└── main.py                              # Main application
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 13+
- Redis 6+
- Docker & Docker Compose

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd b2b-attribution-platform
```

2. **Environment Setup**
```bash
# Copy environment template
cp .env.template .env

# Edit configuration
nano .env
```

3. **Docker Deployment**
```bash
# Start all services
docker-compose up -d

# Initialize database
docker-compose exec backend python -m alembic upgrade head
```

4. **Manual Setup (Development)**
```bash
# Install dependencies
pip install -r requirements.txt

# Start backend
cd backend
uvicorn app.main:app --reload --port 8000

# Start frontend
cd frontend  
streamlit run main.py --server.port 8501
```

## 📖 Usage Guide

### 🎯 B2B Attribution Analysis

#### 1. Access the Platform
- Navigate to `http://localhost:8501`
- Go to "🎯 B2B Attribution" in the sidebar

#### 2. Configure Analysis Parameters
- **Date Range**: Select analysis period
- **Account Filtering**: Choose enterprise, mid-market, or SMB
- **Custom Weights**: Adjust attribution factor weights
- **Account IDs**: Specify particular accounts to analyze

#### 3. Run Attribution Analysis
```python
# API Example
POST /attribution/b2b/calculate
{
  "account_ids": ["account_123", "account_456"],
  "date_from": "2024-01-01",
  "date_to": "2024-12-31",
  "attribution_weights": {
    "time": 0.3,
    "quality": 0.25,
    "account": 0.25,
    "stage": 0.15,
    "velocity": 0.05
  }
}
```

#### 4. Analyze Results
- **Attribution Overview**: Total value and touchpoint counts
- **Model Comparison**: Different attribution perspectives
- **Top Touchpoints**: Highest contributing interactions
- **Detailed Breakdown**: Individual model results

### 📊 Channel Performance Analysis

#### 1. Generate Channel Insights
```python
POST /attribution/b2b/channel-insights
{
  "account_ids": ["account_123"],
  "date_from": "2024-01-01",
  "date_to": "2024-12-31"
}
```

#### 2. Review Performance Metrics
- **ROI by Channel**: Return on investment analysis
- **Cost Efficiency**: Cost per attribution dollar
- **Volume Analysis**: Touchpoint frequency
- **Optimization Recommendations**: Actionable insights

### 🤝 Sales-Marketing Alignment

#### 1. Generate Alignment Report
```python
POST /attribution/b2b/alignment-report
{
  "date_from": "2024-01-01",
  "date_to": "2024-12-31"
}
```

#### 2. Interpret Results
- **Alignment Score**: 0-100 scale assessment
- **Grade**: Letter grade (A+ to F)
- **Attribution Split**: Sales vs Marketing vs Joint
- **Recommendations**: Specific improvement actions

## 🔧 API Reference

### Authentication
All API endpoints require authentication via JWT tokens.

### Core Endpoints

#### Calculate B2B Attribution
```http
POST /attribution/b2b/calculate
Content-Type: application/json
Authorization: Bearer <token>

{
  "account_ids": ["string"],
  "date_from": "2024-01-01",
  "date_to": "2024-12-31",
  "attribution_weights": {
    "time": 0.25,
    "quality": 0.25,
    "account": 0.25,
    "stage": 0.15,
    "velocity": 0.10
  }
}
```

#### Channel Performance Insights
```http
POST /attribution/b2b/channel-insights
Content-Type: application/json
Authorization: Bearer <token>

{
  "account_ids": ["string"],
  "date_from": "2024-01-01",
  "date_to": "2024-12-31"
}
```

#### Sales-Marketing Alignment
```http
POST /attribution/b2b/alignment-report
Content-Type: application/json
Authorization: Bearer <token>

{
  "account_ids": ["string"],
  "date_from": "2024-01-01",
  "date_to": "2024-12-31"
}
```

#### Model Information
```http
GET /attribution/b2b/model-info
Authorization: Bearer <token>
```

#### Touchpoint Types
```http
GET /attribution/b2b/touchpoint-types
Authorization: Bearer <token>
```

## 🧪 Testing

### Run B2B Attribution Tests
```bash
# All B2B attribution tests
pytest tests/test_b2b_attribution_engine.py -v

# Specific test categories
pytest tests/test_b2b_attribution_engine.py::TestB2BMarketingAttributionEngine -v
pytest tests/test_b2b_attribution_engine.py::TestB2BAttributionAnalyzer -v

# Performance tests
pytest tests/test_b2b_attribution_engine.py -k "performance" -v

# Edge case tests
pytest tests/test_b2b_attribution_engine.py::TestB2BEdgeCases -v
```

### Test Coverage
```bash
# Generate coverage report
pytest tests/test_b2b_attribution_engine.py --cov=backend/app/services/b2b_attribution_engine --cov-report=html

# View coverage
open htmlcov/index.html
```

## 📊 Data Model

### Lead Data Structure
```python
@dataclass
class LeadData:
    lead_id: str
    account_id: str
    lead_score: int                    # 0-100 lead quality score
    demographic_score: int             # 0-100 demographic fit
    behavioral_score: int              # 0-100 behavioral indicators
    firmographic_score: int            # 0-100 company fit
    created_date: datetime
    stage: B2BStageType               # Current funnel stage
    source: str                       # Lead source
    lead_quality_tier: str            # A, B, C, D tier
```

### Opportunity Data Structure
```python
@dataclass
class OpportunityData:
    opportunity_id: str
    account_id: str
    lead_ids: List[str]               # Associated leads
    stage: str                        # Current deal stage
    probability: float                # Close probability
    amount: float                     # Deal value
    created_date: datetime
    close_date: Optional[datetime]
    sales_cycle_days: int             # Actual cycle length
    deal_size_tier: str               # enterprise, mid-market, smb
    decision_makers_count: int        # Buying committee size
    influencers_count: int            # Additional stakeholders
```

### Touchpoint Data Structure
```python
@dataclass
class TouchpointData:
    touchpoint_id: str
    lead_id: str
    account_id: str
    timestamp: datetime
    touchpoint_type: TouchpointType   # B2B touchpoint category
    channel: str                      # Marketing channel
    campaign_id: Optional[str]        # Campaign identifier
    content_id: Optional[str]         # Content piece
    engagement_score: float           # 0-100 engagement level
    stage_influence: B2BStageType     # Funnel stage impact
    cost: float                       # Associated cost
    is_sales_touch: bool              # Sales team interaction
    is_marketing_touch: bool          # Marketing team interaction
    sales_rep_id: Optional[str]       # Sales representative
```

## 🎯 B2B Attribution Models

### 1. Time-Weighted Attribution
```python
# B2B-specific decay for long sales cycles
half_life_days = max(sales_cycle_days * 0.3, 14)
weight = math.exp(-days_to_conversion / half_life_days)
```

### 2. Lead Quality Attribution
```python
# Quality multipliers by tier
quality_multipliers = {
    'A': 1.5,  # High-quality leads
    'B': 1.2,  # Medium-quality leads  
    'C': 1.0,  # Standard leads
    'D': 0.7   # Low-quality leads
}
```

### 3. Account-Based Attribution
```python
# Account complexity factors
complexity_factors = [
    deal_size_tier,           # Enterprise, mid-market, SMB
    committee_size,           # Number of decision makers
    sales_cycle_length,       # Actual vs expected cycle
    stakeholder_count         # Total influencers
]
```

### 4. Stage Progression Weights
```python
stage_weights = {
    'AWARENESS': 0.8,
    'INTEREST': 1.0,
    'CONSIDERATION': 1.2,
    'INTENT': 1.4,
    'EVALUATION': 1.5,
    'PURCHASE': 1.3
}
```

### 5. Pipeline Velocity Impact
```python
# Velocity bonus calculation
if actual_cycle < expected_cycle:
    velocity_bonus = 1 + ((expected_cycle - actual_cycle) / expected_cycle) * 0.5
else:
    velocity_bonus = max(0.5, 1 - ((actual_cycle - expected_cycle) / expected_cycle) * 0.3)
```

## 📈 Performance Optimization

### Query Optimization
- Indexed database queries for large datasets
- Async processing for concurrent attribution calculations
- Caching of intermediate results

### Scalability Features  
- Horizontal scaling support via Redis
- Background job processing with Celery
- Database connection pooling
- API rate limiting

### Memory Management
- Streaming data processing for large datasets
- Batch processing for bulk operations
- Efficient data structures for attribution calculations

## 🔒 Security

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (RBAC)
- API key management for service accounts

### Data Protection
- Encryption at rest and in transit
- GDPR compliance features
- Audit logging for all operations
- Secure configuration management

## 🚀 Deployment

### Production Deployment with Docker
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  backend:
    image: b2b-attribution-backend:latest
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/attribution
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
  
  frontend:
    image: b2b-attribution-frontend:latest
    environment:
      - API_BASE_URL=http://backend:8000
    depends_on:
      - backend
  
  postgres:
    image: postgres:13
    environment:
      - POSTGRES_DB=attribution
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:6-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Kubernetes Deployment
```yaml
# k8s/attribution-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: b2b-attribution-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: b2b-attribution-backend
  template:
    metadata:
      labels:
        app: b2b-attribution-backend
    spec:
      containers:
      - name: backend
        image: b2b-attribution-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
```

## 📊 Monitoring & Observability

### Metrics Collection
- Prometheus metrics for performance monitoring
- Grafana dashboards for visualization
- Custom B2B attribution metrics

### Logging
- Structured JSON logging
- Centralized log aggregation
- Attribution calculation audit trails

### Health Checks
- API endpoint health monitoring
- Database connection health
- Redis connectivity checks

## 🤝 Contributing

### Development Setup
```bash
# Clone and setup
git clone <repository-url>
cd b2b-attribution-platform

# Install development dependencies
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install

# Run tests
pytest tests/ -v
```

### Code Quality
- Type hints throughout codebase
- Comprehensive unit test coverage (>90%)
- Integration tests for API endpoints
- Performance tests for attribution calculations

### Pull Request Process
1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Run quality checks
5. Submit pull request with description

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Documentation
- [API Documentation](docs/api.md)
- [User Guide](docs/user-guide.md)
- [Developer Guide](docs/developer-guide.md)

### Community
- [GitHub Issues](https://github.com/your-org/b2b-attribution/issues)
- [Discussions](https://github.com/your-org/b2b-attribution/discussions)
- [Wiki](https://github.com/your-org/b2b-attribution/wiki)

### Enterprise Support
For enterprise support, custom implementations, or consulting services, contact our team.

---

**Built with ❤️ for B2B Marketing Teams**

This platform is specifically designed to solve the complex attribution challenges faced by B2B organizations with long sales cycles, multiple stakeholders, and sophisticated go-to-market strategies.
