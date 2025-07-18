#!/usr/bin/env python3
"""
Multi-Touch Attribution Platform - Startup Script

This script provides easy project initialization and deployment options.
"""
import os
import sys
import subprocess
import argparse
import time
from pathlib import Path


def run_command(command: str, capture_output: bool = False, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command with proper error handling."""
    print(f"🔄 Running: {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=capture_output,
            text=True,
            check=check
        )
        if capture_output and result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {e}")
        if capture_output and e.stderr:
            print(f"Error: {e.stderr}")
        raise


def check_requirements():
    """Check if required tools are installed."""
    print("🔍 Checking requirements...")
    
    requirements = {
        "docker": "docker --version",
        "docker-compose": "docker-compose --version",
        "python": "python3 --version",
        "git": "git --version"
    }
    
    missing = []
    for tool, command in requirements.items():
        try:
            run_command(command, capture_output=True)
            print(f"✅ {tool} is installed")
        except subprocess.CalledProcessError:
            print(f"❌ {tool} is not installed")
            missing.append(tool)
    
    if missing:
        print(f"\n⚠️  Missing requirements: {', '.join(missing)}")
        print("Please install the missing tools and try again.")
        return False
    
    print("✅ All requirements met!")
    return True


def setup_environment():
    """Setup the development environment."""
    print("🛠️  Setting up environment...")
    
    # Create .env file if it doesn't exist
    env_path = Path(".env")
    if not env_path.exists():
        print("📄 Creating .env file...")
        env_content = """# Multi-Touch Attribution Platform Environment Variables

# Environment
ENVIRONMENT=development
TESTING=false

# Database
DB_URL=postgresql://attribution_user:attribution_password@localhost:5432/attribution_db
DB_ECHO=false

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=20

# API Settings
API_SECRET_KEY=your-super-secret-key-change-in-production
API_DEBUG=true
API_CORS_ORIGINS=http://localhost:3000,http://localhost:8501

# Attribution Settings
ATTRIBUTION_DEFAULT_MODELS=first_touch,last_touch,linear,time_decay,u_shaped,w_shaped
ATTRIBUTION_LOOKBACK_WINDOW_DAYS=90
ATTRIBUTION_TIME_DECAY_HALF_LIFE=7

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Streamlit
STREAMLIT_API_BASE_URL=http://localhost:8000
STREAMLIT_TITLE=Multi-Touch Attribution Analytics

# Logging
LOG_LEVEL=INFO
LOG_FILE_PATH=logs/app.log

# Feature Flags
ENABLE_CACHING=true
ENABLE_RATE_LIMITING=true
ENABLE_METRICS=true
"""
        env_path.write_text(env_content)
        print("✅ .env file created")
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    print("✅ Logs directory created")
    
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    print("✅ Data directory created")


def start_development():
    """Start development environment."""
    print("🚀 Starting development environment...")
    
    # Start database and Redis
    print("📦 Starting database and Redis...")
    run_command("docker-compose up -d postgres redis")
    
    # Wait for services to be ready
    print("⏳ Waiting for services to be ready...")
    time.sleep(10)
    
    print("\n✅ Development environment started!")
    print("\n📋 Next steps:")
    print("1. Backend: cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print("2. Frontend: cd frontend && streamlit run main.py")
    print("3. Celery Worker: celery -A backend.app.core.celery worker --loglevel=info")
    print("\n🌐 URLs:")
    print("- Backend API: http://localhost:8000")
    print("- API Docs: http://localhost:8000/docs")
    print("- Frontend: http://localhost:8501")


def start_production():
    """Start production environment with Docker Compose."""
    print("🚀 Starting production environment...")
    
    # Build and start all services
    run_command("docker-compose up -d --build")
    
    # Wait for services to be ready
    print("⏳ Waiting for services to be ready...")
    time.sleep(30)
    
    # Check service health
    print("🔍 Checking service health...")
    run_command("docker-compose ps")
    
    print("\n✅ Production environment started!")
    print("\n🌐 URLs:")
    print("- Frontend: http://localhost:8501")
    print("- Backend API: http://localhost:8000")
    print("- API Documentation: http://localhost:8000/docs")
    print("- Monitoring (Grafana): http://localhost:3000")
    print("- Task Monitor (Flower): http://localhost:5555")


def stop_services():
    """Stop all services."""
    print("🛑 Stopping services...")
    run_command("docker-compose down")
    print("✅ Services stopped!")


def run_tests():
    """Run the test suite."""
    print("🧪 Running tests...")
    
    # Install test dependencies
    run_command("pip install -r requirements.txt")
    
    # Run tests
    run_command("pytest tests/ -v --cov=backend --cov=frontend --cov-report=html")
    
    print("✅ Tests completed!")


def run_linting():
    """Run code linting and formatting."""
    print("🔍 Running code linting...")
    
    # Install dev dependencies
    run_command("pip install black flake8 mypy")
    
    # Run formatters and linters
    run_command("black backend/ frontend/ config/ tests/")
    run_command("flake8 backend/ frontend/ config/")
    run_command("mypy backend/ config/")
    
    print("✅ Linting completed!")


def deploy():
    """Deploy to cloud platform."""
    print("☁️  Deploying to cloud...")
    
    # Build Docker images
    run_command("docker-compose -f docker-compose.prod.yml build")
    
    # Push images (requires Docker registry configuration)
    print("📤 Pushing Docker images...")
    run_command("docker-compose -f docker-compose.prod.yml push", check=False)
    
    print("✅ Deployment process initiated!")
    print("Note: Configure your cloud platform settings for complete deployment.")


def show_logs():
    """Show application logs."""
    print("📋 Showing application logs...")
    run_command("docker-compose logs -f --tail=100")


def show_status():
    """Show system status."""
    print("📊 System Status")
    print("=" * 50)
    
    # Docker services
    print("\n🐳 Docker Services:")
    run_command("docker-compose ps", check=False)
    
    # Disk usage
    print("\n💾 Disk Usage:")
    run_command("df -h | head -5", check=False)
    
    # Memory usage
    print("\n🧠 Memory Usage:")
    run_command("free -h", check=False)
    
    # Check API health
    print("\n🔍 API Health Check:")
    run_command("curl -s http://localhost:8000/health || echo 'API not reachable'", check=False)


def cleanup():
    """Clean up development environment."""
    print("🧹 Cleaning up...")
    
    # Stop services
    run_command("docker-compose down")
    
    # Remove volumes (optional)
    response = input("Remove data volumes? (y/N): ")
    if response.lower() == 'y':
        run_command("docker-compose down -v")
        print("✅ Volumes removed")
    
    # Clean Docker images
    response = input("Remove Docker images? (y/N): ")
    if response.lower() == 'y':
        run_command("docker system prune -f")
        print("✅ Docker images cleaned")
    
    print("✅ Cleanup completed!")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Multi-Touch Attribution Platform Startup Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/start.py --dev          # Start development environment
  python scripts/start.py --prod         # Start production environment
  python scripts/start.py --test         # Run tests
  python scripts/start.py --status       # Show status
  python scripts/start.py --cleanup      # Clean up environment
        """
    )
    
    parser.add_argument("--check", action="store_true", help="Check requirements")
    parser.add_argument("--setup", action="store_true", help="Setup environment")
    parser.add_argument("--dev", action="store_true", help="Start development environment")
    parser.add_argument("--prod", action="store_true", help="Start production environment")
    parser.add_argument("--stop", action="store_true", help="Stop all services")
    parser.add_argument("--test", action="store_true", help="Run tests")
    parser.add_argument("--lint", action="store_true", help="Run linting")
    parser.add_argument("--deploy", action="store_true", help="Deploy to cloud")
    parser.add_argument("--logs", action="store_true", help="Show logs")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--cleanup", action="store_true", help="Clean up environment")
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    print("🎯 Multi-Touch Attribution Platform")
    print("=" * 50)
    
    try:
        if args.check:
            check_requirements()
        elif args.setup:
            setup_environment()
        elif args.dev:
            if not check_requirements():
                return
            setup_environment()
            start_development()
        elif args.prod:
            if not check_requirements():
                return
            setup_environment()
            start_production()
        elif args.stop:
            stop_services()
        elif args.test:
            run_tests()
        elif args.lint:
            run_linting()
        elif args.deploy:
            deploy()
        elif args.logs:
            show_logs()
        elif args.status:
            show_status()
        elif args.cleanup:
            cleanup()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Operation interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()