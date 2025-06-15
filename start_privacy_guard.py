#!/usr/bin/env python3
"""
Privacy Guard System Launcher

This script helps start all the required services for the privacy guard system.
It can start services individually or all together.
"""

import subprocess
import sys
import os
import time
import argparse
import signal
from pathlib import Path

class ServiceManager:
    def __init__(self):
        self.processes = {}
        self.base_dir = Path(__file__).parent
        
    def start_face_detection(self, model_path: str, api_host: str = "127.0.0.1", api_port: int = 8000):
        """Start the face detection service."""
        print(f"Starting face detection service on {api_host}:{api_port}...")
        
        if not os.path.exists(model_path):
            print(f"Error: Model file not found at {model_path}")
            return False
            
        face_detect_dir = self.base_dir / "face-detect"
        if not face_detect_dir.exists():
            print(f"Error: Face detection directory not found at {face_detect_dir}")
            return False
            
        cmd = [
            sys.executable, "-m", "face_counter",
            "--model-path", model_path,
            "--api-host", api_host,
            "--api-port", str(api_port)
        ]
        
        try:
            process = subprocess.Popen(
                cmd,
                cwd=face_detect_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes['face_detection'] = process
            print(f"✅ Face detection service started (PID: {process.pid})")
            return True
        except Exception as e:
            print(f"❌ Failed to start face detection service: {e}")
            return False
    
    def start_central_server(self, port: int = 3000):
        """Start the central server for browser extension data."""
        print(f"Starting central server on port {port}...")
        
        central_server_dir = self.base_dir / "central-server"
        if not central_server_dir.exists():
            print(f"Error: Central server directory not found at {central_server_dir}")
            return False
            
        # Check if package.json exists
        package_json = central_server_dir / "package.json"
        if not package_json.exists():
            print(f"Error: package.json not found at {package_json}")
            return False
            
        # Check if node_modules exists, if not run npm install
        node_modules = central_server_dir / "node_modules"
        if not node_modules.exists():
            print("Installing npm dependencies...")
            install_process = subprocess.run(
                ["npm", "install"],
                cwd=central_server_dir,
                capture_output=True,
                text=True
            )
            if install_process.returncode != 0:
                print(f"❌ Failed to install npm dependencies: {install_process.stderr}")
                return False
            print("✅ npm dependencies installed")
        
        try:
            env = os.environ.copy()
            env['PORT'] = str(port)
            
            process = subprocess.Popen(
                ["npm", "start"],
                cwd=central_server_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes['central_server'] = process
            print(f"✅ Central server started (PID: {process.pid})")
            return True
        except Exception as e:
            print(f"❌ Failed to start central server: {e}")
            return False
    
    def start_privacy_guard(self, **kwargs):
        """Start the unified privacy guard script."""
        print("Starting unified privacy guard...")
        
        privacy_guard_script = self.base_dir / "unified_privacy_guard.py"
        if not privacy_guard_script.exists():
            print(f"Error: Privacy guard script not found at {privacy_guard_script}")
            return False
            
        cmd = [sys.executable, str(privacy_guard_script)]
        
        # Add command line arguments
        if 'face_api_url' in kwargs:
            cmd.extend(['--face-api-url', kwargs['face_api_url']])
        if 'browser_server_url' in kwargs:
            cmd.extend(['--browser-server-url', kwargs['browser_server_url']])
        if 'llm_url' in kwargs:
            cmd.extend(['--llm-url', kwargs['llm_url']])
        if 'check_interval' in kwargs:
            cmd.extend(['--check-interval', str(kwargs['check_interval'])])
        if kwargs.get('test_once'):
            cmd.append('--test-once')
            
        try:
            process = subprocess.Popen(
                cmd,
                cwd=self.base_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            self.processes['privacy_guard'] = process
            print(f"✅ Privacy guard started (PID: {process.pid})")
            return True
        except Exception as e:
            print(f"❌ Failed to start privacy guard: {e}")
            return False
    
    def stop_all(self):
        """Stop all running services."""
        print("\nStopping all services...")
        
        for service_name, process in self.processes.items():
            if process and process.poll() is None:  # Process is still running
                print(f"Stopping {service_name} (PID: {process.pid})...")
                try:
                    process.terminate()
                    process.wait(timeout=5)
                    print(f"✅ {service_name} stopped")
                except subprocess.TimeoutExpired:
                    print(f"⚠️  Force killing {service_name}...")
                    process.kill()
                    process.wait()
                    print(f"✅ {service_name} force stopped")
                except Exception as e:
                    print(f"❌ Error stopping {service_name}: {e}")
        
        self.processes.clear()
        print("All services stopped")
    
    def status(self):
        """Check status of all services."""
        print("\nService Status:")
        print("-" * 50)
        
        if not self.processes:
            print("No services running")
            return
            
        for service_name, process in self.processes.items():
            if process.poll() is None:
                print(f"✅ {service_name}: Running (PID: {process.pid})")
            else:
                print(f"❌ {service_name}: Stopped (Exit code: {process.returncode})")
    
    def wait_for_services(self):
        """Wait for all services and handle shutdown gracefully."""
        def signal_handler(signum, frame):
            print(f"\nReceived signal {signum}")
            self.stop_all()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            print("\nAll services started. Press Ctrl+C to stop all services.")
            print("Use 'python start_privacy_guard.py --status' to check service status.")
            
            while True:
                time.sleep(1)
                # Check if any critical process has died
                dead_services = []
                for service_name, process in self.processes.items():
                    if process.poll() is not None:
                        dead_services.append(service_name)
                
                if dead_services:
                    print(f"\n⚠️  Services died: {', '.join(dead_services)}")
                    self.status()
                    break
                    
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_all()

def main():
    parser = argparse.ArgumentParser(description="Privacy Guard System Launcher")
    
    # Service selection
    parser.add_argument('--face-only', action='store_true', help='Start only face detection service')
    parser.add_argument('--server-only', action='store_true', help='Start only central server')
    parser.add_argument('--guard-only', action='store_true', help='Start only privacy guard')
    parser.add_argument('--status', action='store_true', help='Check service status')
    
    # Face detection options
    parser.add_argument('--model-path', required=False, help='Path to ONNX model file for face detection')
    parser.add_argument('--face-api-host', default='127.0.0.1', help='Face detection API host')
    parser.add_argument('--face-api-port', type=int, default=8000, help='Face detection API port')
    
    # Central server options
    parser.add_argument('--server-port', type=int, default=3000, help='Central server port')
    
    # Privacy guard options
    parser.add_argument('--face-api-url', default='http://127.0.0.1:8000/face-count', help='Face detection API URL')
    parser.add_argument('--browser-server-url', default='http://localhost:3000/api/storage', help='Browser server URL')
    parser.add_argument('--llm-url', default='http://localhost:3001/api/v1/openai/chat/completions', help='LLM API URL')
    parser.add_argument('--check-interval', type=float, default=2.0, help='Privacy guard check interval')
    parser.add_argument('--test-once', action='store_true', help='Run privacy guard once and exit')
    
    args = parser.parse_args()
    
    manager = ServiceManager()
    
    if args.status:
        manager.status()
        return
    
    success = True
    
    # Start individual services or all services
    if args.face_only:
        if not args.model_path:
            print("Error: --model-path is required for face detection service")
            sys.exit(1)
        success = manager.start_face_detection(args.model_path, args.face_api_host, args.face_api_port)
    elif args.server_only:
        success = manager.start_central_server(args.server_port)
    elif args.guard_only:
        guard_kwargs = {
            'face_api_url': args.face_api_url,
            'browser_server_url': args.browser_server_url,
            'llm_url': args.llm_url,
            'check_interval': args.check_interval,
            'test_once': args.test_once
        }
        success = manager.start_privacy_guard(**guard_kwargs)
    else:
        # Start all services
        print("Starting all Privacy Guard services...")
        print("=" * 50)
        
        # Start face detection
        if args.model_path:
            success &= manager.start_face_detection(args.model_path, args.face_api_host, args.face_api_port)
            time.sleep(2)  # Give face detection time to start
        else:
            print("⚠️  Skipping face detection (no --model-path provided)")
        
        # Start central server
        success &= manager.start_central_server(args.server_port)
        time.sleep(2)  # Give server time to start
        
        # Start privacy guard
        guard_kwargs = {
            'face_api_url': args.face_api_url,
            'browser_server_url': args.browser_server_url,
            'llm_url': args.llm_url,
            'check_interval': args.check_interval,
            'test_once': args.test_once
        }
        success &= manager.start_privacy_guard(**guard_kwargs)
    
    if not success:
        print("\n❌ Some services failed to start")
        manager.stop_all()
        sys.exit(1)
    
    if not args.test_once:
        manager.wait_for_services()

if __name__ == "__main__":
    main()
