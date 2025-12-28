#!/usr/bin/env python3
"""
Local Docker Test Script for Hugging Face Spaces
Run this before deploying to verify everything works
"""
import os
import sys
import subprocess
import time
import requests
from pathlib import Path

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_status(message, status="info"):
    """Print colored status message"""
    colors = {
        "success": GREEN,
        "error": RED,
        "warning": YELLOW,
        "info": BLUE
    }
    color = colors.get(status, RESET)
    symbol = "✅" if status == "success" else "❌" if status == "error" else "⚠️" if status == "warning" else "ℹ️"
    print(f"{color}{symbol} {message}{RESET}")

def check_docker():
    """Check if Docker is installed and running"""
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print_status(f"Docker installed: {result.stdout.strip()}", "success")
            return True
    except FileNotFoundError:
        print_status("Docker is not installed. Please install Docker first.", "error")
        return False
    return False

def check_required_files():
    """Check if all required files exist"""
    required_files = [
        'Dockerfile',
        'requirements.txt',
        'main.py',
        'app/__init__.py',
        'app/config.py',
        'app/database.py',
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
            print_status(f"Missing: {file}", "error")
        else:
            print_status(f"Found: {file}", "success")
    
    return len(missing_files) == 0

def check_env_variables():
    """Check if required environment variables are set"""
    required_vars = ['DATABASE_URL', 'SECRET_KEY']
    missing_vars = []
    
    for var in required_vars:
        if os.getenv(var):
            print_status(f"{var} is set", "success")
        else:
            missing_vars.append(var)
            print_status(f"{var} is NOT set", "warning")
    
    if missing_vars:
        print_status("Some environment variables are missing. App will use fallback values.", "warning")
        print_status("This is OK for local testing, but REQUIRED for production.", "info")
    
    return True

def build_docker_image():
    """Build Docker image"""
    print_status("Building Docker image (this may take 5-10 minutes)...", "info")
    
    try:
        result = subprocess.run(
            ['docker', 'build', '-t', 'rating-prediction-test', '.'],
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print_status("Docker image built successfully", "success")
            return True
        else:
            print_status("Docker build failed", "error")
            return False
    except Exception as e:
        print_status(f"Build error: {str(e)}", "error")
        return False

def run_docker_container():
    """Run Docker container"""
    print_status("Starting Docker container...", "info")
    
    # Prepare environment variables
    env_vars = []
    if os.getenv('DATABASE_URL'):
        env_vars.extend(['-e', f"DATABASE_URL={os.getenv('DATABASE_URL')}"])
    if os.getenv('SECRET_KEY'):
        env_vars.extend(['-e', f"SECRET_KEY={os.getenv('SECRET_KEY')}"])
    
    cmd = [
        'docker', 'run', '-d',
        '--name', 'rating-prediction-test',
        '-p', '7860:7860',
        *env_vars,
        'rating-prediction-test'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            container_id = result.stdout.strip()
            print_status(f"Container started: {container_id[:12]}", "success")
            return container_id
        else:
            print_status(f"Container start failed: {result.stderr}", "error")
            return None
    except Exception as e:
        print_status(f"Run error: {str(e)}", "error")
        return None

def wait_for_app(max_wait=60):
    """Wait for app to become ready"""
    print_status(f"Waiting for app to start (max {max_wait}s)...", "info")
    
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            response = requests.get('http://localhost:7860/docs', timeout=5)
            if response.status_code == 200:
                print_status("App is ready!", "success")
                return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(2)
        print(".", end="", flush=True)
    
    print()
    print_status("App did not start in time", "error")
    return False

def test_endpoints():
    """Test key API endpoints"""
    print_status("Testing API endpoints...", "info")
    
    tests = [
        ('GET', '/docs', 200, 'Swagger UI'),
        ('GET', '/api/auth/login', 405, 'Auth endpoint (405 expected for GET)'),
    ]
    
    passed = 0
    failed = 0
    
    for method, endpoint, expected_status, description in tests:
        try:
            url = f'http://localhost:7860{endpoint}'
            if method == 'GET':
                response = requests.get(url, timeout=10)
            else:
                response = requests.post(url, timeout=10)
            
            if response.status_code == expected_status:
                print_status(f"{description}: {response.status_code}", "success")
                passed += 1
            else:
                print_status(f"{description}: Expected {expected_status}, got {response.status_code}", "error")
                failed += 1
        except Exception as e:
            print_status(f"{description}: {str(e)}", "error")
            failed += 1
    
    return passed, failed

def show_logs():
    """Show container logs"""
    print_status("Container logs (last 20 lines):", "info")
    try:
        result = subprocess.run(
            ['docker', 'logs', '--tail', '20', 'rating-prediction-test'],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
    except Exception as e:
        print_status(f"Could not fetch logs: {str(e)}", "error")

def cleanup():
    """Clean up test container and image"""
    print_status("Cleaning up...", "info")
    
    # Stop and remove container
    subprocess.run(['docker', 'stop', 'rating-prediction-test'], 
                   capture_output=True, stderr=subprocess.DEVNULL)
    subprocess.run(['docker', 'rm', 'rating-prediction-test'], 
                   capture_output=True, stderr=subprocess.DEVNULL)
    
    # Optionally remove image
    response = input("\nRemove Docker image? (y/N): ")
    if response.lower() == 'y':
        subprocess.run(['docker', 'rmi', 'rating-prediction-test'], 
                       capture_output=True)
        print_status("Image removed", "success")

def main():
    """Main test flow"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Hugging Face Spaces - Local Docker Test{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    # Step 1: Check Docker
    if not check_docker():
        sys.exit(1)
    
    # Step 2: Check files
    print("\n--- Checking Required Files ---")
    if not check_required_files():
        print_status("Some required files are missing. Cannot proceed.", "error")
        sys.exit(1)
    
    # Step 3: Check environment variables
    print("\n--- Checking Environment Variables ---")
    check_env_variables()
    
    # Step 4: Build image
    print("\n--- Building Docker Image ---")
    if not build_docker_image():
        sys.exit(1)
    
    # Step 5: Run container
    print("\n--- Starting Container ---")
    container_id = run_docker_container()
    if not container_id:
        sys.exit(1)
    
    try:
        # Step 6: Wait for app
        print("\n--- Waiting for Application ---")
        if not wait_for_app():
            show_logs()
            sys.exit(1)
        
        # Step 7: Test endpoints
        print("\n--- Testing Endpoints ---")
        passed, failed = test_endpoints()
        
        # Step 8: Show logs
        print("\n--- Container Logs ---")
        show_logs()
        
        # Results
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{GREEN if failed == 0 else RED}Test Results:{RESET}")
        print(f"  ✅ Passed: {passed}")
        print(f"  ❌ Failed: {failed}")
        print(f"{BLUE}{'='*60}{RESET}\n")
        
        if failed == 0:
            print_status("All tests passed! Ready for Hugging Face deployment. 🚀", "success")
            print_status("Access the app at: http://localhost:7860", "info")
            print_status("Press Ctrl+C when done testing", "info")
            
            # Keep container running
            input("\nPress Enter to stop container and cleanup...")
        else:
            print_status("Some tests failed. Review logs above.", "error")
    
    finally:
        # Cleanup
        cleanup()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        cleanup()
    except Exception as e:
        print_status(f"Unexpected error: {str(e)}", "error")
        cleanup()
        sys.exit(1)
