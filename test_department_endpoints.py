#!/usr/bin/env python3
"""
Department Endpoints Test Script
Tests all the new department-related API endpoints to ensure they're working correctly.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

def print_test_header(test_name):
    """Print a formatted test header"""
    print(f"\n{'='*60}")
    print(f"Testing: {test_name}")
    print(f"{'='*60}")

def print_response(response, show_full=False):
    """Print response details"""
    print(f"Status Code: {response.status_code}")
    
    try:
        data = response.json()
        if show_full:
            print("Response:")
            print(json.dumps(data, indent=2))
        else:
            # Show summary for large responses
            if 'departments' in data:
                print(f"Found {len(data['departments'])} departments")
                for dept in data['departments']:
                    print(f"  - {dept['name']}: {dept['product_count']} products")
            elif 'department' in data:
                dept = data['department']
                print(f"Department: {dept['name']} ({dept['product_count']} products)")
                if 'top_categories' in dept:
                    print(f"Top categories: {[cat['category'] for cat in dept['top_categories'][:3]]}")
            elif 'products' in data:
                print(f"Found {len(data['products'])} products")
                if 'pagination' in data:
                    p = data['pagination']
                    print(f"Page {p['page']} of {p['total_pages']} (Total: {p['total_count']} products)")
                if 'filters' in data:
                    active_filters = {k: v for k, v in data['filters'].items() if v is not None}
                    if active_filters:
                        print(f"Active filters: {active_filters}")
            else:
                print("Response:")
                print(json.dumps(data, indent=2))
    except:
        print("Response Text:")
        print(response.text)

def test_get_departments():
    """Test GET /api/departments"""
    print_test_header("GET /api/departments - List all departments")
    
    try:
        response = requests.get(f"{API_BASE}/departments")
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            assert 'departments' in data
            assert 'total_departments' in data
            assert len(data['departments']) > 0
            print("✅ Test passed!")
        else:
            print("❌ Test failed!")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

def test_get_department_details():
    """Test GET /api/departments/{id}"""
    print_test_header("GET /api/departments/1 - Get Men department details")
    
    try:
        response = requests.get(f"{API_BASE}/departments/1")
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            assert 'department' in data
            dept = data['department']
            assert dept['name'] == 'Men'
            assert 'product_count' in dept
            assert 'top_categories' in dept
            assert 'top_brands' in dept
            print("✅ Test passed!")
        else:
            print("❌ Test failed!")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

def test_get_department_not_found():
    """Test GET /api/departments/{id} for non-existent department"""
    print_test_header("GET /api/departments/999 - Test 404 error handling")
    
    try:
        response = requests.get(f"{API_BASE}/departments/999")
        print_response(response)
        
        if response.status_code == 404:
            data = response.json()
            assert 'error' in data
            assert data['error'] == 'Department not found'
            print("✅ Test passed!")
        else:
            print("❌ Test failed! Expected 404 status code")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

def test_get_department_products():
    """Test GET /api/departments/{id}/products"""
    print_test_header("GET /api/departments/1/products - Get Men department products")
    
    try:
        response = requests.get(f"{API_BASE}/departments/1/products?limit=5")
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            assert 'products' in data
            assert 'department_id' in data
            assert 'department_name' in data
            assert 'pagination' in data
            assert data['department_name'] == 'Men'
            assert len(data['products']) <= 5
            print("✅ Test passed!")
        else:
            print("❌ Test failed!")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

def test_department_products_filtering():
    """Test filtering in department products"""
    print_test_header("GET /api/departments/1/products with filters")
    
    try:
        # Test category filter
        response = requests.get(f"{API_BASE}/departments/1/products?category=Jeans&limit=3")
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            assert all(product['category'] == 'Jeans' for product in data['products'])
            print("✅ Category filter test passed!")
        else:
            print("❌ Category filter test failed!")
            
        # Test price range filter
        print("\n" + "-"*40)
        print("Testing price range filter...")
        response = requests.get(f"{API_BASE}/departments/1/products?min_price=50&max_price=100&limit=3")
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            for product in data['products']:
                price = product['retail_price']
                assert 50 <= price <= 100, f"Product price {price} not in range 50-100"
            print("✅ Price filter test passed!")
        else:
            print("❌ Price filter test failed!")
            
        # Test search filter
        print("\n" + "-"*40)
        print("Testing search filter...")
        response = requests.get(f"{API_BASE}/departments/1/products?search=Calvin&limit=3")
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            for product in data['products']:
                assert 'Calvin' in product['name'] or 'Calvin' in product['brand']
            print("✅ Search filter test passed!")
        else:
            print("❌ Search filter test failed!")
            
    except Exception as e:
        print(f"❌ Filter tests failed with error: {e}")

def test_department_products_not_found():
    """Test GET /api/departments/{id}/products for non-existent department"""
    print_test_header("GET /api/departments/999/products - Test 404 error handling")
    
    try:
        response = requests.get(f"{API_BASE}/departments/999/products")
        print_response(response)
        
        if response.status_code == 404:
            data = response.json()
            assert 'error' in data
            assert data['error'] == 'Department not found'
            print("✅ Test passed!")
        else:
            print("❌ Test failed! Expected 404 status code")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

def test_department_products_pagination():
    """Test pagination in department products"""
    print_test_header("Testing pagination in department products")
    
    try:
        # Get first page
        response = requests.get(f"{API_BASE}/departments/1/products?page=1&limit=5")
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            pagination = data['pagination']
            assert pagination['page'] == 1
            assert pagination['limit'] == 5
            assert pagination['has_next'] == True
            assert pagination['has_prev'] == False
            print("✅ First page test passed!")
            
            # Get second page
            response = requests.get(f"{API_BASE}/departments/1/products?page=2&limit=5")
            if response.status_code == 200:
                data = response.json()
                pagination = data['pagination']
                assert pagination['page'] == 2
                assert pagination['has_prev'] == True
                print("✅ Second page test passed!")
            else:
                print("❌ Second page test failed!")
        else:
            print("❌ Pagination test failed!")
            
    except Exception as e:
        print(f"❌ Pagination test failed with error: {e}")

def main():
    """Run all tests"""
    print("🧪 Starting Department Endpoints Test Suite")
    print(f"Testing API at: {API_BASE}")
    print(f"Test started at: {datetime.now().isoformat()}")
    
    # Check if API is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ API health check failed! Make sure the API server is running.")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API! Make sure the server is running on localhost:5000")
        sys.exit(1)
    
    # Run all tests
    test_get_departments()
    test_get_department_details()
    test_get_department_not_found()
    test_get_department_products()
    test_department_products_filtering()
    test_department_products_not_found()
    test_department_products_pagination()
    
    print("\n" + "="*60)
    print("🎉 All tests completed!")
    print("="*60)

if __name__ == "__main__":
    main()
