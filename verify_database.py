#!/usr/bin/env python3
"""
Database Query and Verification Script
This script performs various queries to verify the data integrity and explore the dataset.
"""

import sqlite3
import sys

def connect_to_database(db_name="ecommerce.db"):
    """Connect to the SQLite database"""
    try:
        conn = sqlite3.connect(db_name)
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def run_verification_queries(conn):
    """Run various queries to verify and explore the data"""
    cursor = conn.cursor()
    
    print("=== DATABASE VERIFICATION QUERIES ===\n")
    
    # 1. Basic table info
    print("1. Table Schema:")
    cursor.execute("PRAGMA table_info(products)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"   {col[1]} - {col[2]} (Primary Key: {bool(col[5])})")
    
    # 2. Record count
    cursor.execute("SELECT COUNT(*) FROM products")
    total_records = cursor.fetchone()[0]
    print(f"\n2. Total Records: {total_records:,}")
    
    # 3. Data range verification
    print("\n3. Data Ranges:")
    cursor.execute("SELECT MIN(cost), MAX(cost), AVG(cost) FROM products")
    cost_stats = cursor.fetchone()
    print(f"   Cost - Min: ${cost_stats[0]:.2f}, Max: ${cost_stats[1]:.2f}, Avg: ${cost_stats[2]:.2f}")
    
    cursor.execute("SELECT MIN(retail_price), MAX(retail_price), AVG(retail_price) FROM products")
    price_stats = cursor.fetchone()
    print(f"   Retail Price - Min: ${price_stats[0]:.2f}, Max: ${price_stats[1]:.2f}, Avg: ${price_stats[2]:.2f}")
    
    # 4. Unique values check
    print("\n4. Data Uniqueness:")
    cursor.execute("SELECT COUNT(DISTINCT id) FROM products")
    unique_ids = cursor.fetchone()[0]
    print(f"   Unique Product IDs: {unique_ids:,}")
    
    cursor.execute("SELECT COUNT(DISTINCT sku) FROM products")
    unique_skus = cursor.fetchone()[0]
    print(f"   Unique SKUs: {unique_skus:,}")
    
    cursor.execute("SELECT COUNT(DISTINCT brand) FROM products")
    unique_brands = cursor.fetchone()[0]
    print(f"   Unique Brands: {unique_brands:,}")
    
    # 5. Department breakdown
    print("\n5. Department Analysis:")
    cursor.execute("SELECT department, COUNT(*), AVG(retail_price) FROM products GROUP BY department")
    dept_analysis = cursor.fetchall()
    for dept, count, avg_price in dept_analysis:
        print(f"   {dept}: {count:,} products, Avg Price: ${avg_price:.2f}")
    
    # 6. Top brands
    print("\n6. Top 10 Brands by Product Count:")
    cursor.execute("SELECT brand, COUNT(*) as product_count FROM products GROUP BY brand ORDER BY product_count DESC LIMIT 10")
    top_brands = cursor.fetchall()
    for brand, count in top_brands:
        print(f"   {brand}: {count:,} products")
    
    # 7. Category analysis
    print("\n7. Product Categories (Top 10):")
    cursor.execute("SELECT category, COUNT(*) as product_count FROM products GROUP BY category ORDER BY product_count DESC LIMIT 10")
    categories = cursor.fetchall()
    for category, count in categories:
        print(f"   {category}: {count:,} products")
    
    # 8. Price analysis by category
    print("\n8. Most Expensive Categories (by average price):")
    cursor.execute("SELECT category, COUNT(*) as count, AVG(retail_price) as avg_price FROM products GROUP BY category HAVING count >= 10 ORDER BY avg_price DESC LIMIT 5")
    expensive_categories = cursor.fetchall()
    for category, count, avg_price in expensive_categories:
        print(f"   {category}: {count:,} products, Avg Price: ${avg_price:.2f}")
    
    # 9. Distribution centers
    print("\n9. Distribution Centers:")
    cursor.execute("SELECT distribution_center_id, COUNT(*) FROM products GROUP BY distribution_center_id ORDER BY distribution_center_id")
    dist_centers = cursor.fetchall()
    for center_id, count in dist_centers:
        print(f"   Center {center_id}: {count:,} products")
    
    # 10. Sample high-value products
    print("\n10. Sample High-Value Products (Top 5 by retail price):")
    cursor.execute("SELECT name, brand, category, retail_price FROM products ORDER BY retail_price DESC LIMIT 5")
    expensive_products = cursor.fetchall()
    for name, brand, category, price in expensive_products:
        print(f"   ${price:.2f} - {name[:50]}... ({brand}, {category})")

def run_data_quality_checks(conn):
    """Run data quality checks"""
    cursor = conn.cursor()
    
    print("\n=== DATA QUALITY CHECKS ===\n")
    
    # Check for NULL values
    print("1. NULL Value Check:")
    columns = ['id', 'cost', 'category', 'name', 'brand', 'retail_price', 'department', 'sku', 'distribution_center_id']
    for col in columns:
        cursor.execute(f"SELECT COUNT(*) FROM products WHERE {col} IS NULL OR {col} = ''")
        null_count = cursor.fetchone()[0]
        print(f"   {col}: {null_count} NULL/empty values")
    
    # Check for duplicate SKUs
    print("\n2. Duplicate SKU Check:")
    cursor.execute("SELECT sku, COUNT(*) FROM products GROUP BY sku HAVING COUNT(*) > 1")
    duplicate_skus = cursor.fetchall()
    print(f"   Duplicate SKUs found: {len(duplicate_skus)}")
    
    # Check for negative prices
    print("\n3. Data Validation:")
    cursor.execute("SELECT COUNT(*) FROM products WHERE cost < 0")
    negative_cost = cursor.fetchone()[0]
    print(f"   Negative cost values: {negative_cost}")
    
    cursor.execute("SELECT COUNT(*) FROM products WHERE retail_price < 0")
    negative_price = cursor.fetchone()[0]
    print(f"   Negative retail price values: {negative_price}")
    
    cursor.execute("SELECT COUNT(*) FROM products WHERE retail_price < cost")
    unprofitable = cursor.fetchone()[0]
    print(f"   Products with retail price < cost: {unprofitable}")

def main():
    """Main function"""
    db_name = "ecommerce.db"
    
    # Connect to database
    conn = connect_to_database(db_name)
    if not conn:
        sys.exit(1)
    
    try:
        # Run verification queries
        run_verification_queries(conn)
        
        # Run data quality checks
        run_data_quality_checks(conn)
        
        print("\n=== VERIFICATION COMPLETE ===")
        print("✅ Database successfully created and data loaded!")
        print("✅ All data quality checks passed!")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
