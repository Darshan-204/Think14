#!/usr/bin/env python3
"""
API Test Script
This script tests all the REST API endpoints to verify they work correctly.
"""

import requests
import json
import time
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:5000"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_response(response, description):
    """Print formatted API response"""
    print(f"\n{description}")
    print("-" * 60)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print("Response (formatted):")
            print(json.dumps(data, indent=2, default=str)[:1000] + "..." if len(str(data)) > 1000 else json.dumps(data, indent=2, default=str))
        except:
            print("Response Text:", response.text[:500])
    else:
        print("Error Response:", response.text)

def test_api():
    """Test all API endpoints"""
    
    print_section("PRODUCTS REST API TEST SUITE")
    print(f"Testing API at: {BASE_URL}")
    print(f"Test started at: {datetime.now()}")
    
    # Wait a moment for server to be ready
    time.sleep(2)
    
    # Test 1: Root endpoint
    print_section("TEST 1: Root Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/")
        print_response(response, "GET /")
    except requests.RequestException as e:
        print(f"Error: {e}")
    
    # Test 2: Health check
    print_section("TEST 2: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print_response(response, "GET /health")
    except requests.RequestException as e:
        print(f"Error: {e}")
    
    # Test 3: Get all products (first page)
    print_section("TEST 3: Get All Products (First Page)")
    try:
        response = requests.get(f"{BASE_URL}/api/products")
        print_response(response, "GET /api/products")
    except requests.RequestException as e:
        print(f"Error: {e}")
    
    # Test 4: Get products with pagination
    print_section("TEST 4: Get Products with Pagination")
    try:
        response = requests.get(f"{BASE_URL}/api/products?page=2&limit=5")
        print_response(response, "GET /api/products?page=2&limit=5")
    except requests.RequestException as e:
        print(f"Error: {e}")
    
    # Test 5: Get products with filters
    print_section("TEST 5: Get Products with Filters")
    try:
        response = requests.get(f"{BASE_URL}/api/products?department=Women&category=Jeans&limit=3")
        print_response(response, "GET /api/products?department=Women&category=Jeans&limit=3")
    except requests.RequestException as e:
        print(f"Error: {e}")
    
    # Test 6: Get products with price filter
    print_section("TEST 6: Get Products with Price Filter")
    try:
        response = requests.get(f"{BASE_URL}/api/products?min_price=100&max_price=200&limit=3")
        print_response(response, "GET /api/products?min_price=100&max_price=200&limit=3")
    except requests.RequestException as e:
        print(f"Error: {e}")
    
    # Test 7: Get products with search
    print_section("TEST 7: Get Products with Search")
    try:
        response = requests.get(f"{BASE_URL}/api/products?search=Calvin&limit=3")
        print_response(response, "GET /api/products?search=Calvin&limit=3")
    except requests.RequestException as e:
        print(f"Error: {e}")
    
    # Test 8: Get products with sorting
    print_section("TEST 8: Get Products with Sorting")
    try:
        response = requests.get(f"{BASE_URL}/api/products?sort_by=retail_price&sort_order=desc&limit=5")
        print_response(response, "GET /api/products?sort_by=retail_price&sort_order=desc&limit=5")
    except requests.RequestException as e:
        print(f"Error: {e}")
    
    # Test 9: Get specific product by ID
    print_section("TEST 9: Get Specific Product by ID")
    try:
        response = requests.get(f"{BASE_URL}/api/products/1")
        print_response(response, "GET /api/products/1")
    except requests.RequestException as e:
        print(f"Error: {e}")
    
    # Test 10: Get product that doesn't exist
    print_section("TEST 10: Get Non-existent Product")
    try:
        response = requests.get(f"{BASE_URL}/api/products/999999")
        print_response(response, "GET /api/products/999999")
    except requests.RequestException as e:
        print(f"Error: {e}")
    
    # Test 11: Get product statistics
    print_section("TEST 11: Get Product Statistics")
    try:
        response = requests.get(f"{BASE_URL}/api/products/stats")
        print_response(response, "GET /api/products/stats")
    except requests.RequestException as e:
        print(f"Error: {e}")
    
    # Test 12: Invalid endpoints
    print_section("TEST 12: Invalid Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/api/invalid")
        print_response(response, "GET /api/invalid")
    except requests.RequestException as e:
        print(f"Error: {e}")
    
    print_section("TEST SUMMARY")
    print("✅ All API endpoints have been tested!")
    print("📋 Check the responses above to verify functionality")
    print("🌐 API is running at: http://localhost:5000")
    print("\nAvailable endpoints:")
    print("  • GET /                     - API information")
    print("  • GET /health               - Health check")
    print("  • GET /api/products         - List products (with filters)")
    print("  • GET /api/products/{id}    - Get specific product")
    print("  • GET /api/products/stats   - Get statistics")

def main():
    """Main function"""
    test_api()

if __name__ == "__main__":
    main()
