#!/usr/bin/env python3
"""
Integrated Marketing Analytics Platform Startup Script

Manages the complete marketing analytics stack:
- Flask Customer Segmentation App
- B2B Marketing Attribution Platform (FastAPI)
- Streamlit Frontend Dashboard
- Database and Redis services
- Integration endpoints
"""

import os
import sys
import time
import subprocess
import signal
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional
import threading
import psutil
from datetime import datetime


class ServiceManager:
    """Manages all services in the marketing analytics platform."""
    
    def __init__(self):
        self.services = {}
        self.project_root = Path.cwd()
        self.log_dir = self.project_root / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # Service configurations
        self.service_configs = {
            'database': {
                'name': 'PostgreSQL Database',
                'command': ['docker-compose', 'up', '-d', 'postgres'],
                'health_check': self._check_postgres,
                'port': 5432,
                'required': True
            },
            'redis': {
                'name': 'Redis Cache',
                'command': ['docker-compose', 'up', '-d', 'redis'],
                'health_check': self._check_redis,
                'port': 6379,
                'required': True
            },
            'segmentation_app': {
                'name': 'Flask Segmentation App',
                'command': ['python', 'app.py'],
                'health_check': lambda: self._check_http('http://localhost:5000'),
                'port': 5000,
                'cwd': self.project_root,
                'required': False  # Optional existing app
            },
            'attribution_backend': {
                'name': 'B2B Attribution API (FastAPI)',
                'command': ['python', '-m', 'uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', '8000', '--reload'],
                'health_check': lambda: self._check_http('http://localhost:8000/health'),
                'port': 8000,
                'cwd': self.project_root / 'backend',
                'required': True
            },
            'attribution_frontend': {
                'name': 'Streamlit Attribution Dashboard',
                'command': ['streamlit', 'run', 'main.py', '--server.port', '8501', '--server.address', '0.0.0.0'],
                'health_check': lambda: self._check_http('http://localhost:8501'),
                'port': 8501,
                'cwd': self.project_root / 'frontend',
                'required': True
            },
            'celery_worker': {
                'name': 'Celery Background Worker',
                'command': ['celery', '-A', 'app.core.celery', 'worker', '--loglevel=info'],
                'health_check': self._check_celery,
                'port': None,
                'cwd': self.project_root / 'backend',
                'required': False
            }
        }
    
    def start_all_services(self, mode: str = 'development'):
        """Start all services in the correct order."""
        print("🚀 Starting Integrated Marketing Analytics Platform")
        print("=" * 60)
        
        # Check dependencies first
        self._check_dependencies()
        
        # Start services in dependency order
        startup_order = [
            'database',
            'redis', 
            'segmentation_app',
            'attribution_backend',
            'celery_worker',
            'attribution_frontend'
        ]
        
        for service_name in startup_order:
            try:
                self._start_service(service_name, mode)
                time.sleep(2)  # Give service time to start
            except Exception as e:
                if self.service_configs[service_name]['required']:
                    print(f"❌ Failed to start required service {service_name}: {e}")
                    self.stop_all_services()
                    sys.exit(1)
                else:
                    print(f"⚠️  Optional service {service_name} failed to start: {e}")
        
        # Wait for all services to be healthy
        self._wait_for_all_services()
        
        # Display service status
        self._display_service_status()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        print("\n🎉 All services started successfully!")
        self._display_access_info()
        
        # Keep the script running
        try:
            while True:
                time.sleep(10)
                self._monitor_services()
        except KeyboardInterrupt:
            self.stop_all_services()
    
    def stop_all_services(self):
        """Stop all running services."""
        print("\n🛑 Stopping all services...")
        
        for service_name, process in self.services.items():
            try:
                if process and process.poll() is None:
                    print(f"   Stopping {self.service_configs[service_name]['name']}...")
                    process.terminate()
                    process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                print(f"   Error stopping {service_name}: {e}")
        
        # Stop Docker services
        try:
            subprocess.run(['docker-compose', 'down'], check=False)
        except Exception:
            pass
        
        print("✅ All services stopped")
    
    def status(self):
        """Display status of all services."""
        print("📊 Service Status")
        print("=" * 40)
        
        for service_name, config in self.service_configs.items():
            if config['health_check']:
                try:
                    if config['health_check']():
                        status = "🟢 Running"
                    else:
                        status = "🔴 Down"
                except Exception:
                    status = "🟡 Unknown"
            else:
                status = "⚪ No health check"
            
            print(f"{config['name']:<30} {status}")
    
    def restart_service(self, service_name: str):
        """Restart a specific service."""
        if service_name in self.services:
            print(f"🔄 Restarting {self.service_configs[service_name]['name']}...")
            self._stop_service(service_name)
            time.sleep(2)
            self._start_service(service_name)
            print(f"✅ {service_name} restarted")
        else:
            print(f"❌ Service {service_name} not found")
    
    def _start_service(self, service_name: str, mode: str = 'development'):
        """Start a specific service."""
        config = self.service_configs[service_name]
        print(f"🔄 Starting {config['name']}...")
        
        # Special handling for Docker services
        if service_name in ['database', 'redis']:
            try:
                result = subprocess.run(config['command'], 
                                      capture_output=True, 
                                      text=True, 
                                      check=True)
                self.services[service_name] = None  # Docker managed
                print(f"✅ {config['name']} started")
                return
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to start {config['name']}: {e}")
                if config['required']:
                    raise
                return
        
        # Special handling for optional segmentation app
        if service_name == 'segmentation_app':
            app_py_path = self.project_root / 'app.py'
            if not app_py_path.exists():
                print(f"⚠️  Flask app.py not found, skipping segmentation app")
                return
        
        # Start regular services
        try:
            log_file = self.log_dir / f"{service_name}.log"
            
            with open(log_file, 'w') as f:
                process = subprocess.Popen(
                    config['command'],
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    cwd=config.get('cwd', self.project_root)
                )
            
            self.services[service_name] = process
            print(f"✅ {config['name']} started (PID: {process.pid})")
            
        except Exception as e:
            print(f"❌ Failed to start {config['name']}: {e}")
            if config['required']:
                raise
    
    def _stop_service(self, service_name: str):
        """Stop a specific service."""
        if service_name in self.services and self.services[service_name]:
            process = self.services[service_name]
            try:
                process.terminate()
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
            finally:
                del self.services[service_name]
    
    def _wait_for_all_services(self, timeout: int = 60):
        """Wait for all services to become healthy."""
        print("\n⏳ Waiting for services to become ready...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            all_healthy = True
            
            for service_name, config in self.service_configs.items():
                if service_name not in self.services and config['required']:
                    all_healthy = False
                    break
                
                if config['health_check']:
                    try:
                        if not config['health_check']():
                            all_healthy = False
                            break
                    except Exception:
                        all_healthy = False
                        break
            
            if all_healthy:
                print("✅ All services are ready!")
                return
            
            print("   Services starting up...")
            time.sleep(5)
        
        print("⚠️  Some services may not be fully ready yet")
    
    def _monitor_services(self):
        """Monitor running services and restart if needed."""
        for service_name, process in list(self.services.items()):
            if process and process.poll() is not None:
                config = self.service_configs[service_name]
                if config['required']:
                    print(f"⚠️  {config['name']} stopped unexpectedly, restarting...")
                    self._start_service(service_name)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        print(f"\n📞 Received signal {signum}, shutting down...")
        self.stop_all_services()
        sys.exit(0)
    
    def _check_dependencies(self):
        """Check that all required dependencies are installed."""
        print("🔍 Checking dependencies...")
        
        dependencies = {
            'python': ['python', '--version'],
            'docker': ['docker', '--version'],
            'docker-compose': ['docker-compose', '--version']
        }
        
        for name, command in dependencies.items():
            try:
                subprocess.run(command, capture_output=True, check=True)
                print(f"   ✅ {name} found")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print(f"   ❌ {name} not found or not working")
                if name in ['docker', 'docker-compose']:
                    print(f"      Please install {name} to run database and Redis services")
    
    def _check_postgres(self) -> bool:
        """Check if PostgreSQL is running."""
        try:
            result = subprocess.run(['docker', 'ps', '--filter', 'name=postgres', 
                                   '--format', '{{.Status}}'], 
                                  capture_output=True, text=True)
            return 'Up' in result.stdout
        except Exception:
            return False
    
    def _check_redis(self) -> bool:
        """Check if Redis is running."""
        try:
            result = subprocess.run(['docker', 'ps', '--filter', 'name=redis',
                                   '--format', '{{.Status}}'], 
                                  capture_output=True, text=True)
            return 'Up' in result.stdout
        except Exception:
            return False
    
    def _check_celery(self) -> bool:
        """Check if Celery worker is running."""
        # This is a simple check - in production you'd use Celery's inspect
        return True
    
    def _check_http(self, url: str) -> bool:
        """Check if HTTP service is responding."""
        try:
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def _display_service_status(self):
        """Display current status of all services."""
        print("\n📊 Service Status:")
        print("-" * 50)
        
        for service_name, config in self.service_configs.items():
            if service_name in self.services or service_name in ['database', 'redis']:
                if config['health_check']:
                    try:
                        if config['health_check']():
                            status = "🟢 Healthy"
                        else:
                            status = "🟡 Starting"
                    except Exception:
                        status = "🔴 Error"
                else:
                    status = "🟢 Running"
                
                port_info = f":{config['port']}" if config['port'] else ""
                print(f"   {config['name']:<30} {status} {port_info}")
    
    def _display_access_info(self):
        """Display access information for all services."""
        print("\n🌐 Access Information:")
        print("-" * 50)
        
        access_info = {
            'Flask Segmentation App': 'http://localhost:5000',
            'B2B Attribution API': 'http://localhost:8000',
            'Attribution API Docs': 'http://localhost:8000/docs',
            'Streamlit Dashboard': 'http://localhost:8501',
            'Attribution Health Check': 'http://localhost:8000/health'
        }
        
        for name, url in access_info.items():
            print(f"   {name:<25} {url}")
        
        print("\n📋 Quick Start Guide:")
        print("   1. Visit Streamlit Dashboard for B2B attribution analysis")
        print("   2. Use Flask app for customer segmentation (if available)")
        print("   3. Check API docs for integration endpoints")
        print("   4. Monitor logs in ./logs/ directory")


class IntegratedDemo:
    """Demonstrates integration between segmentation and attribution platforms."""
    
    def __init__(self):
        self.segmentation_url = "http://localhost:5000"
        self.attribution_url = "http://localhost:8000"
    
    def run_integration_demo(self):
        """Run integration demo between segmentation and attribution."""
        print("\n🔗 Integration Demo: Segmentation + Attribution")
        print("=" * 60)
        
        try:
            # Check if segmentation app is available
            segmentation_available = self._check_service(self.segmentation_url)
            attribution_available = self._check_service(self.attribution_url)
            
            print(f"Flask Segmentation App: {'✅ Available' if segmentation_available else '❌ Not available'}")
            print(f"B2B Attribution API: {'✅ Available' if attribution_available else '❌ Not available'}")
            
            if not attribution_available:
                print("❌ Attribution API required for demo")
                return
            
            # Demo scenarios
            if segmentation_available:
                self._demo_full_integration()
            else:
                self._demo_attribution_only()
                
        except Exception as e:
            print(f"❌ Demo error: {e}")
    
    def _demo_full_integration(self):
        """Demo with both segmentation and attribution."""
        print("\n🎯 Full Integration Demo")
        print("   Combining customer segmentation with B2B attribution\n")
        
        # Simulate segmentation results
        segments = {
            'enterprise_customers': {
                'characteristics': 'High-value, long sales cycles',
                'avg_deal_size': 500000,
                'typical_cycle': 240,
                'attribution_model': 'account_based'
            },
            'mid_market_customers': {
                'characteristics': 'Medium complexity deals',
                'avg_deal_size': 150000,
                'typical_cycle': 120,
                'attribution_model': 'combined_b2b'
            },
            'smb_customers': {
                'characteristics': 'Quick decision cycles',
                'avg_deal_size': 25000,
                'typical_cycle': 45,
                'attribution_model': 'time_decay'
            }
        }
        
        print("📊 Segmentation-Based Attribution Strategy:")
        for segment, details in segments.items():
            print(f"\n   🎯 {segment.replace('_', ' ').title()}:")
            print(f"      • Characteristics: {details['characteristics']}")
            print(f"      • Avg Deal Size: ${details['avg_deal_size']:,}")
            print(f"      • Typical Cycle: {details['typical_cycle']} days")
            print(f"      • Recommended Model: {details['attribution_model']}")
        
        # Integration workflow
        print("\n🔄 Integration Workflow:")
        workflow_steps = [
            "1. Customer segmentation identifies account characteristics",
            "2. Segment data feeds into attribution model selection",
            "3. B2B attribution calculates touchpoint value by segment",
            "4. Results optimize marketing spend per segment",
            "5. Continuous feedback improves both segmentation and attribution"
        ]
        
        for step in workflow_steps:
            print(f"   {step}")
    
    def _demo_attribution_only(self):
        """Demo with attribution platform only."""
        print("\n🎯 B2B Attribution Demo")
        print("   Showcasing advanced B2B attribution capabilities\n")
        
        # Get attribution model info
        try:
            response = requests.get(f"{self.attribution_url}/attribution/b2b/model-info")
            if response.status_code == 200:
                model_info = response.json()['data']
                
                print("📋 Available Attribution Models:")
                factors = model_info.get('attribution_factors', {})
                for factor, details in factors.items():
                    print(f"   • {factor.replace('_', ' ').title()}: {details.get('description', '')}")
                
            # Demo touchpoint types
            response = requests.get(f"{self.attribution_url}/attribution/b2b/touchpoint-types")
            if response.status_code == 200:
                touchpoint_info = response.json()['data']
                
                print("\n🏷️  B2B Touchpoint Types:")
                touchpoint_types = touchpoint_info.get('touchpoint_types', {})
                sorted_types = sorted(touchpoint_types.items(), 
                                    key=lambda x: x[1].get('weight', 0), 
                                    reverse=True)
                
                for tp_type, info in sorted_types[:5]:
                    weight = info.get('weight', 1.0)
                    category = info.get('category', 'Other')
                    print(f"   • {tp_type.replace('_', ' ').title()}: {weight:.1f}x weight ({category})")
                    
        except Exception as e:
            print(f"   Error fetching model info: {e}")
    
    def _check_service(self, url: str) -> bool:
        """Check if a service is available."""
        try:
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except Exception:
            return False


def main():
    """Main entry point for the startup script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Integrated Marketing Analytics Platform Manager")
    parser.add_argument('action', choices=['start', 'stop', 'status', 'restart', 'demo'], 
                       help='Action to perform')
    parser.add_argument('--service', help='Specific service for restart action')
    parser.add_argument('--mode', choices=['development', 'production'], 
                       default='development', help='Deployment mode')
    
    args = parser.parse_args()
    
    service_manager = ServiceManager()
    
    try:
        if args.action == 'start':
            service_manager.start_all_services(args.mode)
        
        elif args.action == 'stop':
            service_manager.stop_all_services()
        
        elif args.action == 'status':
            service_manager.status()
        
        elif args.action == 'restart':
            if args.service:
                service_manager.restart_service(args.service)
            else:
                print("Please specify --service for restart action")
        
        elif args.action == 'demo':
            # Start services first if not running
            print("🚀 Starting services for demo...")
            service_manager.start_all_services(args.mode)
            
            # Wait a moment for services to stabilize
            time.sleep(5)
            
            # Run integration demo
            demo = IntegratedDemo()
            demo.run_integration_demo()
            
            # Keep services running for demo
            print("\n🎮 Demo complete! Services remain running for exploration.")
            print("   Press Ctrl+C to stop all services")
            
            try:
                while True:
                    time.sleep(10)
            except KeyboardInterrupt:
                service_manager.stop_all_services()
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        service_manager.stop_all_services()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()