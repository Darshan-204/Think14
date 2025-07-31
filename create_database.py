#!/usr/bin/env python3
"""
Database Setup and CSV Data Loading Script
This script creates a SQLite database and loads product data from CSV file.
"""

import sqlite3
import csv
import os
import sys

def create_database_connection(db_name="ecommerce.db"):
    """Create a database connection to SQLite database"""
    try:
        conn = sqlite3.connect(db_name)
        print(f"Successfully connected to {db_name}")
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def create_products_table(conn):
    """Create the products table with appropriate schema"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        cost REAL NOT NULL,
        category TEXT NOT NULL,
        name TEXT NOT NULL,
        brand TEXT NOT NULL,
        retail_price REAL NOT NULL,
        department TEXT NOT NULL,
        sku TEXT UNIQUE NOT NULL,
        distribution_center_id INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    try:
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
        conn.commit()
        print("Products table created successfully")
        return True
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")
        return False

def load_csv_data(conn, csv_file_path):
    """Load data from CSV file into the products table"""
    if not os.path.exists(csv_file_path):
        print(f"CSV file not found: {csv_file_path}")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM products")
        
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            insert_sql = """
            INSERT INTO products (id, cost, category, name, brand, retail_price, 
                                department, sku, distribution_center_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            records_loaded = 0
            for row in csv_reader:
                try:
                    cursor.execute(insert_sql, (
                        int(row['id']),
                        float(row['cost']),
                        row['category'],
                        row['name'],
                        row['brand'],
                        float(row['retail_price']),
                        row['department'],
                        row['sku'],
                        int(row['distribution_center_id'])
                    ))
                    records_loaded += 1
                except (ValueError, KeyError) as e:
                    print(f"Error processing row: {row}. Error: {e}")
                    continue
            
            conn.commit()
            print(f"Successfully loaded {records_loaded} records into products table")
            return True
            
    except sqlite3.Error as e:
        print(f"Error loading CSV data: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def verify_data(conn):
    """Verify the data was loaded correctly"""
    try:
        cursor = conn.cursor()
        
        # Count total records
        cursor.execute("SELECT COUNT(*) FROM products")
        total_count = cursor.fetchone()[0]
        print(f"\nTotal records in database: {total_count}")
        
        # Show sample records
        cursor.execute("SELECT * FROM products LIMIT 5")
        records = cursor.fetchall()
        print("\nSample records:")
        print("ID | Cost | Category | Name | Brand | Retail Price | Department | SKU | Dist Center")
        print("-" * 100)
        for record in records:
            print(f"{record[0]} | {record[1]:.2f} | {record[2]} | {record[3][:20]}... | {record[4]} | {record[5]:.2f} | {record[6]} | {record[7][:10]}... | {record[8]}")
        
        # Show statistics
        cursor.execute("SELECT department, COUNT(*) FROM products GROUP BY department")
        dept_stats = cursor.fetchall()
        print(f"\nRecords by department:")
        for dept, count in dept_stats:
            print(f"  {dept}: {count} products")
        
        cursor.execute("SELECT category, COUNT(*) FROM products GROUP BY category ORDER BY COUNT(*) DESC LIMIT 5")
        category_stats = cursor.fetchall()
        print(f"\nTop 5 categories by product count:")
        for category, count in category_stats:
            print(f"  {category}: {count} products")
            
        return True
        
    except sqlite3.Error as e:
        print(f"Error verifying data: {e}")
        return False

def main():
    """Main function to orchestrate the database setup and data loading"""
    # File paths
    csv_file_path = r"archive (1)\archive\products.csv"
    db_name = "ecommerce.db"
    
    print("=== E-commerce Database Setup ===")
    print(f"Loading data from: {csv_file_path}")
    print(f"Database: {db_name}")
    print()
    
    # Create database connection
    conn = create_database_connection(db_name)
    if not conn:
        sys.exit(1)
    
    try:
        # Create products table
        if not create_products_table(conn):
            sys.exit(1)
        
        # Load CSV data
        if not load_csv_data(conn, csv_file_path):
            sys.exit(1)
        
        # Verify data
        if not verify_data(conn):
            sys.exit(1)
            
        print("\n=== Database setup completed successfully! ===")
        
    finally:
        conn.close()
        print("Database connection closed.")

if __name__ == "__main__":
    main()
