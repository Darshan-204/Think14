#!/usr/bin/env python3
"""
Database Table Structure Display Script
This script shows the detailed structure of the products table.
"""

import sqlite3
import sys

def display_table_structure(db_name="ecommerce.db"):
    """Display detailed table structure information"""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        print("=" * 80)
        print("                    PRODUCTS TABLE STRUCTURE")
        print("=" * 80)
        
        # Get table info
        cursor.execute("PRAGMA table_info(products)")
        columns = cursor.fetchall()
        
        print("\nCOLUMN DEFINITIONS:")
        print("-" * 80)
        print(f"{'Column Name':<25} {'Data Type':<15} {'Nullable':<10} {'Default':<15} {'PK':<5}")
        print("-" * 80)
        
        for col in columns:
            cid, name, data_type, not_null, default_value, pk = col
            nullable = "NO" if not_null else "YES"
            default = str(default_value) if default_value else "NULL"
            primary_key = "YES" if pk else "NO"
            print(f"{name:<25} {data_type:<15} {nullable:<10} {default:<15} {primary_key:<5}")
        
        # Get indexes
        print(f"\nINDEXES:")
        print("-" * 80)
        cursor.execute("PRAGMA index_list(products)")
        indexes = cursor.fetchall()
        
        if indexes:
            for index in indexes:
                index_name = index[1]
                unique = "UNIQUE" if index[2] else "NON-UNIQUE"
                print(f"Index: {index_name} ({unique})")
                
                # Get index details
                cursor.execute(f"PRAGMA index_info('{index_name}')")
                index_info = cursor.fetchall()
                for info in index_info:
                    col_name = info[2]
                    print(f"  - Column: {col_name}")
        else:
            print("No custom indexes found (only automatic primary key index)")
        
        # Show table creation SQL
        print(f"\nTABLE CREATION SQL:")
        print("-" * 80)
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='products'")
        create_sql = cursor.fetchone()
        if create_sql:
            formatted_sql = create_sql[0].replace(',', ',\n    ')
            print(formatted_sql)
        
        # Show table statistics
        print(f"\nTABLE STATISTICS:")
        print("-" * 80)
        
        cursor.execute("SELECT COUNT(*) FROM products")
        total_rows = cursor.fetchone()[0]
        print(f"Total Rows: {total_rows:,}")
        
        # Get table size (approximate)
        cursor.execute("PRAGMA page_size")
        page_size = cursor.fetchone()[0]
        cursor.execute("PRAGMA page_count")
        page_count = cursor.fetchone()[0]
        table_size_bytes = page_size * page_count
        table_size_mb = table_size_bytes / (1024 * 1024)
        print(f"Approximate Table Size: {table_size_mb:.2f} MB")
        
        # Column statistics
        print(f"\nCOLUMN STATISTICS:")
        print("-" * 80)
        
        # Numeric columns
        numeric_columns = ['id', 'cost', 'retail_price', 'distribution_center_id']
        for col in numeric_columns:
            cursor.execute(f"SELECT MIN({col}), MAX({col}), AVG({col}) FROM products")
            min_val, max_val, avg_val = cursor.fetchone()
            if avg_val is not None:
                print(f"{col}:")
                print(f"  Min: {min_val}")
                print(f"  Max: {max_val}")
                print(f"  Avg: {avg_val:.2f}")
        
        # Text columns - unique counts
        text_columns = ['category', 'brand', 'department']
        for col in text_columns:
            cursor.execute(f"SELECT COUNT(DISTINCT {col}) FROM products")
            unique_count = cursor.fetchone()[0]
            print(f"{col}: {unique_count} unique values")
        
        # SKU uniqueness
        cursor.execute("SELECT COUNT(DISTINCT sku) FROM products")
        unique_skus = cursor.fetchone()[0]
        print(f"sku: {unique_skus} unique values (should match total rows)")
        
        print("=" * 80)
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Main function"""
    display_table_structure()

if __name__ == "__main__":
    main()
