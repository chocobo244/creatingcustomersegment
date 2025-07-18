# 🚀 Quick Start Guide - Integrated Marketing Analytics Platform

Get up and running with the complete marketing analytics stack including customer segmentation and B2B attribution in under 10 minutes!

## 📋 Prerequisites

Before starting, ensure you have:

- **Python 3.9+** installed
- **Docker & Docker Compose** for database services
- **Git** for repository management
- **8GB+ RAM** recommended for full stack

### Quick Dependency Check
```bash
python --version    # Should be 3.9+
docker --version    # Required for database
docker-compose --version  # Required for services
```

## ⚡ Option 1: Automated Setup (Recommended)

### 1. Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install additional startup script dependencies
pip install requests psutil
```

### 2. Start Everything with One Command
```bash
# Start all services
python scripts/startup.py start

# Or run with integrated demo
python scripts/startup.py demo
```

This will automatically:
- ✅ Start PostgreSQL and Redis (via Docker)
- ✅ Launch Flask segmentation app (if `app.py` exists)
- ✅ Start B2B Attribution FastAPI backend
- ✅ Launch Streamlit frontend dashboard
- ✅ Start Celery worker for background tasks
- ✅ Run health checks and display access URLs

### 3. Access Your Applications

Once started, you'll see:

```
🌐 Access Information:
--------------------------------------------------
   Flask Segmentation App    http://localhost:5000
   B2B Attribution API       http://localhost:8000
   Attribution API Docs      http://localhost:8000/docs
   Streamlit Dashboard       http://localhost:8501
   Attribution Health Check  http://localhost:8000/health
```

### 4. Stop All Services
```bash
python scripts/startup.py stop
```

## 🛠️ Option 2: Manual Setup

### 1. Start Database Services
```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis
```

### 2. Start Flask Segmentation App (Optional)
```bash
# If you have an existing Flask app
python app.py
# Access at: http://localhost:5000
```

### 3. Start B2B Attribution Backend
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# Access at: http://localhost:8000
```

### 4. Start Streamlit Frontend
```bash
cd frontend
streamlit run main.py --server.port 8501
# Access at: http://localhost:8501
```

### 5. Optional: Start Celery Worker
```bash
cd backend
celery -A app.core.celery worker --loglevel=info
```

## 🎯 Quick Demo Walkthrough

### 1. B2B Attribution Dashboard
Visit **http://localhost:8501** and explore:

- **🎯 B2B Attribution** tab - Main attribution analysis
- **📊 Channel Performance** - ROI insights by channel  
- **🤝 Sales-Marketing Alignment** - Team collaboration metrics
- **🔄 Pipeline Velocity** - Deal acceleration analysis
- **⚙️ Model Configuration** - Attribution model settings

### 2. API Exploration
Visit **http://localhost:8000/docs** to explore:

- `POST /attribution/b2b/calculate` - Main attribution endpoint
- `POST /attribution/b2b/channel-insights` - Channel performance  
- `POST /attribution/b2b/alignment-report` - Sales-marketing alignment
- `GET /attribution/b2b/model-info` - Model configuration
- `GET /attribution/b2b/touchpoint-types` - Touchpoint weights

### 3. Integration Demo
```bash
# Run complete integration demo
python demo_script.py

# Or use startup script demo
python scripts/startup.py demo
```

## 📊 Sample Data & Testing

### Generate Demo Data
```bash
# Run the comprehensive demo with realistic B2B data
python demo_script.py
```

This creates:
- **18 B2B accounts** (Enterprise, Mid-Market, SMB)
- **36 leads** with quality scoring
- **27 opportunities** with realistic deal sizes
- **200+ touchpoints** across different types

### API Testing Examples

#### Calculate B2B Attribution
```bash
curl -X POST "http://localhost:8000/attribution/b2b/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "date_from": "2024-01-01",
    "date_to": "2024-12-31",
    "attribution_weights": {
      "time": 0.25,
      "quality": 0.25,
      "account": 0.25,
      "stage": 0.15,
      "velocity": 0.10
    }
  }'
```

#### Get Channel Insights
```bash
curl -X POST "http://localhost:8000/attribution/b2b/channel-insights" \
  -H "Content-Type: application/json" \
  -d '{
    "date_from": "2024-01-01",
    "date_to": "2024-12-31"
  }'
```

## 🔗 Integration with Existing Systems

### Flask Segmentation App Integration

If you have an existing Flask segmentation app:

1. **Ensure `app.py` exists** in the project root
2. **Start with startup script** - it will auto-detect and launch
3. **Access both platforms**:
   - Segmentation: http://localhost:5000  
   - Attribution: http://localhost:8501

### Integration Workflow

```python
# Example: Using segmentation results for attribution
import requests

# 1. Get segmentation results
segments = requests.get("http://localhost:5000/api/segments").json()

# 2. Apply segment-specific attribution
for segment in segments:
    attribution_request = {
        "account_ids": segment["account_ids"],
        "attribution_weights": segment["recommended_weights"]
    }
    
    # 3. Calculate B2B attribution for segment
    attribution = requests.post(
        "http://localhost:8000/attribution/b2b/calculate",
        json=attribution_request
    ).json()
```

## 🎮 Service Management

### Check Service Status
```bash
python scripts/startup.py status
```

### Restart Specific Service
```bash
python scripts/startup.py restart --service attribution_backend
```

### View Logs
```bash
# Logs are automatically saved to ./logs/
tail -f logs/attribution_backend.log
tail -f logs/attribution_frontend.log
```

## 🏢 Enterprise Features Showcase

### B2B Attribution Models
- **Time-Weighted**: Long sales cycle optimization (3-18 months)
- **Lead Quality**: A/B/C/D tier scoring integration
- **Account-Based**: Enterprise buying committee analysis
- **Stage Progression**: Funnel advancement tracking
- **Pipeline Velocity**: Deal acceleration measurement

### Touchpoint Types & Weights
- **Demo Requests**: 1.5x weight (high intent)
- **Sales Calls**: 1.4x weight (direct sales)
- **Referrals**: 1.6x weight (highest trust)
- **Webinars**: 1.2x weight (education)
- **Content Downloads**: 1.1x weight (research)

### Deal Size Tiers
- **Enterprise**: $200K+ deals, 180-400 day cycles
- **Mid-Market**: $50K-250K deals, 90-200 day cycles  
- **SMB**: $5K-60K deals, 30-90 day cycles

## 🔧 Troubleshooting

### Common Issues

#### Services Won't Start
```bash
# Check if ports are in use
netstat -tulpn | grep :8000
netstat -tulpn | grep :8501
netstat -tulpn | grep :5000

# Kill conflicting processes if needed
sudo kill -9 <PID>
```

#### Database Connection Issues
```bash
# Restart Docker services
docker-compose down
docker-compose up -d postgres redis

# Check Docker status
docker-compose ps
```

#### Attribution API Not Responding
```bash
# Check backend logs
tail -f logs/attribution_backend.log

# Restart backend service
python scripts/startup.py restart --service attribution_backend
```

#### Frontend Issues
```bash
# Check Streamlit logs
tail -f logs/attribution_frontend.log

# Restart frontend
python scripts/startup.py restart --service attribution_frontend
```

### Performance Optimization

#### For Large Datasets
```bash
# Increase Docker memory allocation
# Edit docker-compose.yml and add:
# deploy:
#   resources:
#     limits:
#       memory: 4G
```

#### For Production Deployment
```bash
# Use production mode
python scripts/startup.py start --mode production

# Or deploy with Docker
docker-compose -f docker-compose.prod.yml up -d
```

## 📈 Next Steps

### 1. Explore Advanced Features
- **Custom attribution weights** in Streamlit dashboard
- **Sales-marketing alignment** analysis and recommendations
- **Channel optimization** insights and ROI analysis
- **Pipeline velocity** tracking and acceleration

### 2. Integration Planning
- **CRM Integration**: Salesforce, HubSpot data sync
- **Marketing Automation**: Email platform integration
- **Analytics Integration**: Google Analytics, Adobe Analytics
- **Custom Data Sources**: API endpoints for your data

### 3. Production Deployment
- **Environment Configuration**: Production settings
- **Security Setup**: Authentication and authorization
- **Monitoring**: Prometheus/Grafana dashboards  
- **Scaling**: Multi-instance deployment

### 4. Custom Development
- **Custom Attribution Models**: Implement domain-specific logic
- **Advanced Visualizations**: Custom dashboard components
- **Integration Endpoints**: Custom API integrations
- **ML Enhancement**: Predictive attribution models

## 📞 Support & Resources

### Documentation
- **API Reference**: http://localhost:8000/docs (when running)
- **User Guide**: See full README.md for comprehensive documentation
- **Architecture Guide**: Review system architecture and components

### Community
- **Issues**: Report bugs and request features
- **Discussions**: Community Q&A and best practices
- **Wiki**: Extended documentation and tutorials

### Enterprise Support
For enterprise implementations, custom development, or consulting:
- **Custom Attribution Models** for your industry
- **Advanced Integration** with your tech stack  
- **Performance Optimization** for scale
- **Training & Onboarding** for your team

---

🎉 **Congratulations!** You now have a complete B2B Marketing Attribution Platform running with customer segmentation integration capabilities. Start exploring the advanced analytics and attribution insights!

**Quick Links:**
- 🎯 **Streamlit Dashboard**: http://localhost:8501
- 📊 **API Documentation**: http://localhost:8000/docs  
- 🔧 **Flask Segmentation**: http://localhost:5000
- 💡 **Demo Script**: `python demo_script.py`