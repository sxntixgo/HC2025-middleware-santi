import pytest
import requests
import time
import subprocess
import os
from pathlib import Path

# Base URLs for each challenge
CHALLENGE_1_URL = "http://localhost:8001"  # Port 8001 for challenge 1
CHALLENGE_2_URL = "http://localhost:8002"  # Port 8002 for challenge 2  
CHALLENGE_3_URL = "http://localhost:8003"  # Port 8003 for challenge 3
CHALLENGE_4_URL = "http://localhost:8004"  # Port 8004 for challenge 4
CHALLENGE_X_URL = "https://localhost:8443" # Port 8443 for challenge x

@pytest.fixture(scope="session")
def wait_for_service():
    """Helper to wait for services to be ready"""
    def _wait_for_service(url, timeout=30):
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=5, verify=False)
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        return False
    return _wait_for_service

@pytest.fixture(scope="session") 
def challenge_1_service(wait_for_service):
    """Start Challenge 1 service and wait for it to be ready"""
    challenge_dir = Path(__file__).parent.parent / "challenge-1"
    
    # Start the service
    process = subprocess.Popen(
        ["docker-compose", "-f", "docker-compose-dev.yml", "up", "-d"],
        cwd=challenge_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    process.wait()
    
    # Wait for service to be ready
    if not wait_for_service(CHALLENGE_1_URL):
        pytest.fail("Challenge 1 service failed to start")
    
    yield CHALLENGE_1_URL
    
    # Cleanup
    subprocess.run(["docker-compose", "down"], cwd=challenge_dir, capture_output=True)

@pytest.fixture(scope="session")
def challenge_2_service(wait_for_service):
    """Start Challenge 2 service and wait for it to be ready"""
    challenge_dir = Path(__file__).parent.parent / "challenge-2"
    
    # Start the service
    process = subprocess.Popen(
        ["docker-compose", "-f", "docker-compose-dev.yml", "up", "-d"],
        cwd=challenge_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    process.wait()
    
    # Wait for service to be ready
    if not wait_for_service(CHALLENGE_2_URL):
        pytest.fail("Challenge 2 service failed to start")
    
    yield CHALLENGE_2_URL
    
    # Cleanup
    subprocess.run(["docker-compose", "down"], cwd=challenge_dir, capture_output=True)

@pytest.fixture(scope="session")
def challenge_3_service(wait_for_service):
    """Start Challenge 3 service and wait for it to be ready"""
    challenge_dir = Path(__file__).parent.parent / "challenge-3"
    
    # Start the service
    process = subprocess.Popen(
        ["docker-compose", "-f", "docker-compose-dev.yml", "up", "-d"],
        cwd=challenge_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    process.wait()
    
    # Wait for service to be ready
    if not wait_for_service(CHALLENGE_3_URL):
        pytest.fail("Challenge 3 service failed to start")
    
    yield CHALLENGE_3_URL
    
    # Cleanup
    subprocess.run(["docker-compose", "down"], cwd=challenge_dir, capture_output=True)

@pytest.fixture(scope="session")
def challenge_4_service(wait_for_service):
    """Start Challenge 4 service and wait for it to be ready"""
    challenge_dir = Path(__file__).parent.parent / "challenge-4"
    
    # Start the service
    process = subprocess.Popen(
        ["docker-compose", "-f", "docker-compose-dev.yml", "up", "-d"],
        cwd=challenge_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    process.wait()
    
    # Wait for service to be ready
    if not wait_for_service(CHALLENGE_4_URL):
        pytest.fail("Challenge 4 service failed to start")
    
    yield CHALLENGE_4_URL
    
    # Cleanup
    subprocess.run(["docker-compose", "down"], cwd=challenge_dir, capture_output=True)

@pytest.fixture(scope="session")
def challenge_x_service(wait_for_service):
    """Start Challenge X service and wait for it to be ready"""
    challenge_dir = Path(__file__).parent.parent / "challenge-x"
    
    # Start the service (challenge-x uses docker-compose-dev.yml for testing)
    process = subprocess.Popen(
        ["docker-compose", "-f", "docker-compose-dev.yml", "up", "-d"],
        cwd=challenge_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    process.wait()
    
    # Wait for service to be ready
    if not wait_for_service(CHALLENGE_X_URL):
        pytest.fail("Challenge X service failed to start")
    
    yield CHALLENGE_X_URL
    
    # Cleanup
    subprocess.run(["docker-compose", "-f", "docker-compose-dev.yml", "down"], cwd=challenge_dir, capture_output=True)