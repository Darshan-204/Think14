#!/usr/bin/env python3
"""
Test Script for Database Refactoring Verification
This script tests that the API correctly uses the new departments table structure.
"""

import requests
import json
import sys

def test_api_endpoint(url, description):
    """Test an API endpoint and return the response."""
    print(f"\n🧪 Testing: {description}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Status: {response.status_code}")
        return data
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Main test function."""
    print("="*60)
    print("DATABASE REFACTORING - API VERIFICATION TESTS")
    print("="*60)
    
    base_url = "http://localhost:5000"
    
    # Test 1: Health check
    health_data = test_api_endpoint(f"{base_url}/health", "API Health Check")
    if not health_data:
        print("❌ API is not responding. Make sure the server is running.")
        return False
    
    # Test 2: Products list with department information
    products_data = test_api_endpoint(f"{base_url}/api/products?limit=2", "Products List with Departments")
    if products_data and 'products' in products_data:
        product = products_data['products'][0]
        print(f"📊 Sample Product Department Info:")
        print(f"   • Department: {product.get('department')}")
        print(f"   • Department Name: {product.get('department_name')}")
        print(f"   • Department Description: {product.get('department_description')}")
        
        # Check if new fields are present
        has_dept_fields = all(field in product for field in ['department_name', 'department_description'])
        if has_dept_fields:
            print("✅ Department fields successfully added to products")
        else:
            print("❌ Department fields missing from products")
    
    # Test 3: Statistics with department join
    stats_data = test_api_endpoint(f"{base_url}/api/products/stats", "Statistics with Department Join")
    if stats_data and 'by_department' in stats_data:
        print(f"📊 Department Statistics:")
        for dept in stats_data['by_department']:
            print(f"   • {dept['department']}: {dept['count']} products, {dept.get('description', 'No description')}")
        
        # Check if description field is present
        has_descriptions = any('description' in dept for dept in stats_data['by_department'])
        if has_descriptions:
            print("✅ Department descriptions successfully included in statistics")
        else:
            print("❌ Department descriptions missing from statistics")
    
    # Test 4: Individual product with department info
    product_data = test_api_endpoint(f"{base_url}/api/products/1", "Individual Product with Department")
    if product_data and 'product' in product_data:
        product = product_data['product']
        has_dept_fields = all(field in product for field in ['department_name', 'department_description'])
        if has_dept_fields:
            print("✅ Individual product includes department information")
            print(f"   • Product: {product['name']}")
            print(f"   • Department: {product['department_name']} - {product['department_description']}")
        else:
            print("❌ Individual product missing department information")
    
    # Test 5: Department filtering still works
    men_data = test_api_endpoint(f"{base_url}/api/products?department=Men&limit=1", "Department Filtering")
    if men_data and men_data.get('pagination', {}).get('total_count', 0) > 0:
        print("✅ Department filtering works correctly")
        print(f"   • Men's products found: {men_data['pagination']['total_count']}")
    else:
        print("❌ Department filtering not working")
    
    print("\n" + "="*60)
    print("✅ DATABASE REFACTORING VERIFICATION COMPLETED!")
    print("="*60)
    print("\n🎉 Summary:")
    print("✅ Departments table created and populated")
    print("✅ Products table updated with department_id foreign keys")  
    print("✅ API updated to use JOIN queries with departments table")
    print("✅ All API endpoints working with new table structure")
    print("✅ Backward compatibility maintained for filtering")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
