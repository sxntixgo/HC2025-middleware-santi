#!/usr/bin/env bash

# WAF Challenge Test Runner
# This script runs comprehensive tests for all WAF bypass challenges (1-4 + X)

set -e  # Exit on any error

echo "🔒 WAF Challenge Test Suite"
echo "=============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

# Install test dependencies if needed
print_status "Setting up test environment..."
cd tests
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt

cd ..

# Function to run tests for a specific challenge
run_challenge_tests() {
    local challenge=$1
    local challenge_dir="challenge-$challenge"
    
    print_status "Testing Challenge $challenge..."
    
    # Navigate to challenge directory and start services
    cd "$challenge_dir"
    
    # Clean up any existing containers
    print_status "Cleaning up existing containers for Challenge $challenge..."
    docker-compose down -v > /dev/null 2>&1 || true
    
    # Start services (challenge-x uses dev compose file to avoid port conflicts)
    print_status "Starting services for Challenge $challenge..."
    if [ "$challenge" == "x" ]; then
        docker-compose -f docker-compose-dev.yml up -d --build
        sleep 15  # Challenge-x with SSL needs more time
    else
        docker-compose -f docker-compose-dev.yml up -d --build
        sleep 10
    fi
    
    cd ..
    
    # Run the tests
    source tests/venv/bin/activate
    if pytest tests/test_challenge_$challenge.py -v; then
        print_success "Challenge $challenge tests PASSED"
        set_test_result $challenge "PASS"
    else
        print_error "Challenge $challenge tests FAILED"
        set_test_result $challenge "FAIL"
    fi
    
    # Clean up
    cd "$challenge_dir"
    docker-compose down -v > /dev/null 2>&1
    
    cd ..
}

# Function to show test summary
show_summary() {
    echo
    echo "=============================="
    echo "🎯 Test Results Summary"
    echo "=============================="
    
    local all_passed=true
    
    for challenge_num in 1 2 3 4 x; do
        result=$(get_test_result $challenge_num)
        if [ "$result" == "PASS" ]; then
            print_success "Challenge $challenge_num: $result"
        else
            print_error "Challenge $challenge_num: $result"
            all_passed=false
        fi
    done
    
    echo "=============================="
    
    if $all_passed; then
        print_success "All WAF challenge tests completed successfully! 🎉"
        echo
        echo "The defensive security challenges are working correctly."
        echo "All bypass techniques are properly demonstrated."
        exit 0
    else
        print_error "Some tests failed. Please check the output above for details."
        exit 1
    fi
}

# Parse command line arguments
if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    echo "Usage: $0 [challenge_number]"
    echo
    echo "Options:"
    echo "  challenge_number    Run tests for specific challenge (1, 2, 3, 4, or x)"
    echo "  --help, -h         Show this help message"
    echo
    echo "Examples:"
    echo "  $0                 # Run all challenge tests (1, 2, 3, 4, x)"
    echo "  $0 1               # Run only Challenge 1 tests"
    echo "  $0 2               # Run only Challenge 2 tests"
    echo "  $0 3               # Run only Challenge 3 tests"
    echo "  $0 4               # Run only Challenge 4 tests"
    echo "  $0 x               # Run only Challenge X tests (Host header bypass)"
    exit 0
fi

# Initialize test results using simple variables
test_result_1=""
test_result_2=""
test_result_3=""
test_result_4=""
test_result_x=""

# Function to set test result
set_test_result() {
    local challenge=$1
    local result=$2
    case $challenge in
        1) test_result_1=$result ;;
        2) test_result_2=$result ;;
        3) test_result_3=$result ;;
        4) test_result_4=$result ;;
        x) test_result_x=$result ;;
    esac
}

# Function to get test result
get_test_result() {
    local challenge=$1
    case $challenge in
        1) echo $test_result_1 ;;
        2) echo $test_result_2 ;;
        3) echo $test_result_3 ;;
        4) echo $test_result_4 ;;
        x) echo $test_result_x ;;
    esac
}

# Run tests
if [ $# -eq 0 ]; then
    # Run all challenges
    print_status "Running tests for all challenges..."
    run_challenge_tests 1
    run_challenge_tests 2
    run_challenge_tests 3
    run_challenge_tests 4
    run_challenge_tests x
    show_summary
elif [ "$1" == "x" ]; then
    # Run challenge-x
    print_status "Running tests for Challenge X only..."
    run_challenge_tests x
    result=$(get_test_result x)
    if [ "$result" == "PASS" ]; then
        print_success "Challenge X test completed successfully!"
        exit 0
    else
        print_error "Challenge X test failed!"
        exit 1
    fi
elif [ "$1" -ge 1 ] && [ "$1" -le 4 ] 2>/dev/null; then
    # Run specific challenge
    print_status "Running tests for Challenge $1 only..."
    run_challenge_tests $1
    result=$(get_test_result $1)
    if [ "$result" == "PASS" ]; then
        print_success "Challenge $1 test completed successfully!"
        exit 0
    else
        print_error "Challenge $1 test failed!"
        exit 1
    fi
else
    print_error "Invalid argument. Use --help for usage information."
    exit 1
fi