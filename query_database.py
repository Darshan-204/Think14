#!/usr/bin/env python3
"""
Interactive Database Query Tool
This script provides an interactive interface to query the products database.
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

def run_predefined_queries(conn):
    """Run some predefined useful queries"""
    cursor = conn.cursor()
    
    queries = {
        "1": {
            "description": "Find all products by a specific brand",
            "sql": "SELECT name, category, retail_price FROM products WHERE brand = ? ORDER BY retail_price DESC",
            "params": ["Calvin Klein"]
        },
        "2": {
            "description": "Find products in a price range",
            "sql": "SELECT name, brand, retail_price FROM products WHERE retail_price BETWEEN ? AND ? ORDER BY retail_price",
            "params": [50, 100]
        },
        "3": {
            "description": "Find most expensive products in each category",
            "sql": """
                SELECT category, name, brand, retail_price 
                FROM products p1 
                WHERE retail_price = (
                    SELECT MAX(retail_price) 
                    FROM products p2 
                    WHERE p2.category = p1.category
                ) 
                ORDER BY retail_price DESC
                LIMIT 10
            """,
            "params": []
        },
        "4": {
            "description": "Find products with highest profit margin",
            "sql": """
                SELECT name, brand, category, cost, retail_price, 
                       (retail_price - cost) as profit,
                       ROUND(((retail_price - cost) / cost * 100), 2) as profit_margin_percent
                FROM products 
                WHERE cost > 0
                ORDER BY profit_margin_percent DESC 
                LIMIT 10
            """,
            "params": []
        },
        "5": {
            "description": "Find products by department and category",
            "sql": "SELECT name, brand, retail_price FROM products WHERE department = ? AND category = ? ORDER BY retail_price DESC",
            "params": ["Women", "Jeans"]
        }
    }
    
    print("=== PREDEFINED QUERIES ===\n")
    
    for key, query in queries.items():
        print(f"{key}. {query['description']}")
        if query['params']:
            print(f"   Parameters: {', '.join(map(str, query['params']))}")
        
        try:
            if query['params']:
                cursor.execute(query['sql'], query['params'])
            else:
                cursor.execute(query['sql'])
            
            results = cursor.fetchall()
            
            if results:
                print(f"   Results ({len(results)} found):")
                for i, result in enumerate(results[:5]):  # Show first 5 results
                    print(f"     {i+1}. {' | '.join(map(str, result))}")
                if len(results) > 5:
                    print(f"     ... and {len(results) - 5} more")
            else:
                print("   No results found")
                
        except sqlite3.Error as e:
            print(f"   Error: {e}")
        
        print()

def run_custom_query(conn, query):
    """Run a custom SQL query"""
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            print(f"Results ({len(results)} found):")
            for i, result in enumerate(results):
                print(f"  {i+1}. {' | '.join(map(str, result))}")
        else:
            print("No results found")
            
    except sqlite3.Error as e:
        print(f"Error executing query: {e}")

def interactive_mode(conn):
    """Interactive query mode"""
    print("\n=== INTERACTIVE MODE ===")
    print("Enter SQL queries (type 'exit' to quit, 'help' for examples)")
    
    examples = [
        "SELECT COUNT(*) FROM products WHERE department = 'Men';",
        "SELECT brand, COUNT(*) FROM products GROUP BY brand ORDER BY COUNT(*) DESC LIMIT 5;",
        "SELECT * FROM products WHERE name LIKE '%Calvin Klein%' LIMIT 3;",
        "SELECT category, AVG(retail_price) FROM products GROUP BY category ORDER BY AVG(retail_price) DESC LIMIT 5;"
    ]
    
    while True:
        try:
            query = input("\nSQL> ").strip()
            
            if query.lower() == 'exit':
                break
            elif query.lower() == 'help':
                print("\nExample queries:")
                for i, example in enumerate(examples, 1):
                    print(f"  {i}. {example}")
                continue
            elif not query:
                continue
                
            run_custom_query(conn, query)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except EOFError:
            break

def main():
    """Main function"""
    db_name = "ecommerce.db"
    
    print("=== E-COMMERCE DATABASE QUERY TOOL ===\n")
    
    # Connect to database
    conn = connect_to_database(db_name)
    if not conn:
        sys.exit(1)
    
    try:
        # Run predefined queries
        run_predefined_queries(conn)
        
        # Interactive mode
        response = input("Would you like to enter interactive mode? (y/n): ").strip().lower()
        if response == 'y' or response == 'yes':
            interactive_mode(conn)
        
        print("\nThank you for using the database query tool!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
