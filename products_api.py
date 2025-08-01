#!/usr/bin/env python3
"""
Products REST API
A Flask-based REST API that provides endpoints for accessing product data from the e-commerce database.
"""

from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import sqlite3
import math
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Enable CORS for all domains on all routes
CORS(app)

# Database configuration
DATABASE = 'ecommerce.db'

def get_db_connection():
    """Get database connection with row factory for dict-like access"""
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        return None

def dict_from_row(row):
    """Convert sqlite3.Row to dictionary"""
    return {key: row[key] for key in row.keys()}

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource was not found',
        'status_code': 404
    }), 404

@app.errorhandler(400)
def bad_request(error):
    """Handle 400 errors"""
    return jsonify({
        'error': 'Bad Request',
        'message': 'The request was invalid',
        'status_code': 400
    }), 400

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An internal server error occurred',
        'status_code': 500
    }), 500

@app.route('/')
def index():
    """API welcome endpoint"""
    return jsonify({
        'message': 'Welcome to the Products REST API',
        'version': '1.0.0',
        'endpoints': {
            'GET /api/products': 'List all products (with pagination)',
            'GET /api/products/{id}': 'Get a specific product by ID',
            'GET /api/products/stats': 'Get product statistics',
            'GET /health': 'API health check'
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM products")
            product_count = cursor.fetchone()[0]
            conn.close()
            
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'product_count': product_count,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'database': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500
    else:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/products', methods=['GET'])
def get_products():
    """
    GET /api/products - List all products with pagination and filtering
    
    Query Parameters:
    - page: Page number (default: 1)
    - limit: Items per page (default: 20, max: 100)
    - category: Filter by category
    - department: Filter by department (Men/Women)
    - brand: Filter by brand
    - min_price: Minimum retail price
    - max_price: Maximum retail price
    - search: Search in product name
    - sort_by: Sort by field (name, price, cost, brand)
    - sort_order: Sort order (asc, desc)
    """
    
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    limit = min(request.args.get('limit', 20, type=int), 100)  # Max 100 items per page
    category = request.args.get('category')
    department = request.args.get('department')
    brand = request.args.get('brand')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    search = request.args.get('search')
    sort_by = request.args.get('sort_by', 'id')
    sort_order = request.args.get('sort_order', 'asc')
    
    # Validate parameters
    if page < 1:
        abort(400)
    
    valid_sort_fields = ['id', 'name', 'retail_price', 'cost', 'brand', 'category']
    if sort_by not in valid_sort_fields:
        sort_by = 'id'
    
    if sort_order not in ['asc', 'desc']:
        sort_order = 'asc'
    
    conn = get_db_connection()
    if not conn:
        abort(500)
    
    try:
        cursor = conn.cursor()
        
        # Build the query
        where_conditions = []
        params = []
        
        if category:
            where_conditions.append("category = ?")
            params.append(category)
        
        if department:
            where_conditions.append("department = ?")
            params.append(department)
        
        if brand:
            where_conditions.append("brand = ?")
            params.append(brand)
        
        if min_price is not None:
            where_conditions.append("retail_price >= ?")
            params.append(min_price)
        
        if max_price is not None:
            where_conditions.append("retail_price <= ?")
            params.append(max_price)
        
        if search:
            where_conditions.append("name LIKE ?")
            params.append(f"%{search}%")
        
        # Build WHERE clause
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # Count total records for pagination
        count_query = f"""
            SELECT COUNT(*) 
            FROM products p
            LEFT JOIN departments d ON p.department_id = d.id
            {where_clause}
        """
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]
        
        # Calculate pagination info
        total_pages = math.ceil(total_count / limit)
        offset = (page - 1) * limit
        
        # Build main query with sorting, pagination, and department join
        query = f"""
            SELECT p.id, p.cost, p.category, p.name, p.brand, p.retail_price, 
                   p.department, p.sku, p.distribution_center_id, p.created_at,
                   d.name as department_name, d.description as department_description
            FROM products p
            LEFT JOIN departments d ON p.department_id = d.id
            {where_clause}
            ORDER BY p.{sort_by} {sort_order.upper()}
            LIMIT ? OFFSET ?
        """
        
        params.extend([limit, offset])
        cursor.execute(query, params)
        products = cursor.fetchall()
        
        # Convert to list of dictionaries
        products_list = [dict_from_row(product) for product in products]
        
        # Build response
        response = {
            'products': products_list,
            'pagination': {
                'page': page,
                'limit': limit,
                'total_count': total_count,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1,
                'next_page': page + 1 if page < total_pages else None,
                'prev_page': page - 1 if page > 1 else None
            },
            'filters': {
                'category': category,
                'department': department,
                'brand': brand,
                'min_price': min_price,
                'max_price': max_price,
                'search': search,
                'sort_by': sort_by,
                'sort_order': sort_order
            }
        }
        
        conn.close()
        return jsonify(response)
        
    except sqlite3.Error as e:
        logger.error(f"Database error in get_products: {e}")
        conn.close()
        abort(500)
    except Exception as e:
        logger.error(f"Error in get_products: {e}")
        conn.close()
        abort(500)

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """
    GET /api/products/{id} - Get a specific product by ID
    """
    
    if product_id <= 0:
        abort(400)
    
    conn = get_db_connection()
    if not conn:
        abort(500)
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, p.cost, p.category, p.name, p.brand, p.retail_price, 
                   p.department, p.sku, p.distribution_center_id, p.created_at,
                   d.name as department_name, d.description as department_description
            FROM products p
            LEFT JOIN departments d ON p.department_id = d.id
            WHERE p.id = ?
        """, (product_id,))
        
        product = cursor.fetchone()
        conn.close()
        
        if product is None:
            return jsonify({
                'error': 'Product not found',
                'message': f'Product with ID {product_id} does not exist',
                'product_id': product_id
            }), 404
        
        return jsonify({
            'product': dict_from_row(product)
        })
        
    except sqlite3.Error as e:
        logger.error(f"Database error in get_product: {e}")
        conn.close()
        abort(500)
    except Exception as e:
        logger.error(f"Error in get_product: {e}")
        conn.close()
        abort(500)

@app.route('/api/products/stats', methods=['GET'])
def get_product_stats():
    """
    GET /api/products/stats - Get product statistics
    """
    
    conn = get_db_connection()
    if not conn:
        abort(500)
    
    try:
        cursor = conn.cursor()
        
        # Overall statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_products,
                MIN(retail_price) as min_price,
                MAX(retail_price) as max_price,
                AVG(retail_price) as avg_price,
                MIN(cost) as min_cost,
                MAX(cost) as max_cost,
                AVG(cost) as avg_cost
            FROM products
        """)
        overall_stats = dict_from_row(cursor.fetchone())
        
        # Department statistics
        cursor.execute("""
            SELECT d.name as department, d.description, 
                   COUNT(p.id) as count, AVG(p.retail_price) as avg_price
            FROM departments d
            LEFT JOIN products p ON d.id = p.department_id
            GROUP BY d.id, d.name, d.description
            ORDER BY count DESC
        """)
        dept_stats = [dict_from_row(row) for row in cursor.fetchall()]
        
        # Category statistics (top 10)
        cursor.execute("""
            SELECT category, COUNT(*) as count, AVG(retail_price) as avg_price
            FROM products 
            GROUP BY category 
            ORDER BY count DESC 
            LIMIT 10
        """)
        category_stats = [dict_from_row(row) for row in cursor.fetchall()]
        
        # Brand statistics (top 10)
        cursor.execute("""
            SELECT brand, COUNT(*) as count, AVG(retail_price) as avg_price
            FROM products 
            GROUP BY brand 
            ORDER BY count DESC 
            LIMIT 10
        """)
        brand_stats = [dict_from_row(row) for row in cursor.fetchall()]
        
        # Distribution center statistics
        cursor.execute("""
            SELECT distribution_center_id, COUNT(*) as count
            FROM products 
            GROUP BY distribution_center_id 
            ORDER BY distribution_center_id
        """)
        dist_center_stats = [dict_from_row(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'overall': overall_stats,
            'by_department': dept_stats,
            'top_categories': category_stats,
            'top_brands': brand_stats,
            'distribution_centers': dist_center_stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except sqlite3.Error as e:
        logger.error(f"Database error in get_product_stats: {e}")
        conn.close()
        abort(500)
    except Exception as e:
        logger.error(f"Error in get_product_stats: {e}")
        conn.close()
        abort(500)

@app.route('/api/departments', methods=['GET'])
def get_departments():
    """
    GET /api/departments - List all departments
    
    Returns all departments with their product counts and basic statistics.
    """
    
    conn = get_db_connection()
    if not conn:
        abort(500)
    
    try:
        cursor = conn.cursor()
        
        # Get all departments with product counts and statistics
        cursor.execute("""
            SELECT 
                d.id,
                d.name,
                d.description,
                d.created_at,
                COUNT(p.id) as product_count,
                AVG(p.retail_price) as avg_price,
                MIN(p.retail_price) as min_price,
                MAX(p.retail_price) as max_price
            FROM departments d
            LEFT JOIN products p ON d.id = p.department_id
            GROUP BY d.id, d.name, d.description, d.created_at
            ORDER BY product_count DESC
        """)
        
        departments = cursor.fetchall()
        conn.close()
        
        # Convert to list of dictionaries
        departments_list = [dict_from_row(dept) for dept in departments]
        
        return jsonify({
            'departments': departments_list,
            'total_departments': len(departments_list),
            'timestamp': datetime.now().isoformat()
        })
        
    except sqlite3.Error as e:
        logger.error(f"Database error in get_departments: {e}")
        conn.close()
        abort(500)
    except Exception as e:
        logger.error(f"Error in get_departments: {e}")
        conn.close()
        abort(500)

@app.route('/api/departments/<int:department_id>', methods=['GET'])
def get_department(department_id):
    """
    GET /api/departments/{id} - Get specific department details
    
    Returns detailed information about a specific department including statistics.
    """
    
    if department_id <= 0:
        abort(400)
    
    conn = get_db_connection()
    if not conn:
        abort(500)
    
    try:
        cursor = conn.cursor()
        
        # Get department details with statistics
        cursor.execute("""
            SELECT 
                d.id,
                d.name,
                d.description,
                d.created_at,
                COUNT(p.id) as product_count,
                AVG(p.retail_price) as avg_price,
                MIN(p.retail_price) as min_price,
                MAX(p.retail_price) as max_price,
                AVG(p.cost) as avg_cost
            FROM departments d
            LEFT JOIN products p ON d.id = p.department_id
            WHERE d.id = ?
            GROUP BY d.id, d.name, d.description, d.created_at
        """, (department_id,))
        
        department = cursor.fetchone()
        
        if department is None:
            conn.close()
            return jsonify({
                'error': 'Department not found',
                'message': f'Department with ID {department_id} does not exist',
                'department_id': department_id
            }), 404
        
        # Get top categories in this department
        cursor.execute("""
            SELECT category, COUNT(*) as count, AVG(retail_price) as avg_price
            FROM products p
            JOIN departments d ON p.department_id = d.id
            WHERE d.id = ?
            GROUP BY category
            ORDER BY count DESC
            LIMIT 5
        """, (department_id,))
        
        top_categories = [dict_from_row(row) for row in cursor.fetchall()]
        
        # Get top brands in this department
        cursor.execute("""
            SELECT brand, COUNT(*) as count, AVG(retail_price) as avg_price
            FROM products p
            JOIN departments d ON p.department_id = d.id
            WHERE d.id = ?
            GROUP BY brand
            ORDER BY count DESC
            LIMIT 5
        """, (department_id,))
        
        top_brands = [dict_from_row(row) for row in cursor.fetchall()]
        
        conn.close()
        
        # Build response
        department_data = dict_from_row(department)
        department_data['top_categories'] = top_categories
        department_data['top_brands'] = top_brands
        
        return jsonify({
            'department': department_data,
            'timestamp': datetime.now().isoformat()
        })
        
    except sqlite3.Error as e:
        logger.error(f"Database error in get_department: {e}")
        conn.close()
        abort(500)
    except Exception as e:
        logger.error(f"Error in get_department: {e}")
        conn.close()
        abort(500)

@app.route('/api/departments/<int:department_id>/products', methods=['GET'])
def get_department_products(department_id):
    """
    GET /api/departments/{id}/products - Get all products in a department
    
    Query Parameters:
    - page: Page number (default: 1)
    - limit: Items per page (default: 20, max: 100)
    - category: Filter by category within the department
    - brand: Filter by brand within the department
    - min_price: Minimum retail price
    - max_price: Maximum retail price
    - search: Search in product name
    - sort_by: Sort by field (name, price, cost, brand)
    - sort_order: Sort order (asc, desc)
    """
    
    if department_id <= 0:
        abort(400)
    
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    limit = min(request.args.get('limit', 20, type=int), 100)
    category = request.args.get('category')
    brand = request.args.get('brand')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    search = request.args.get('search')
    sort_by = request.args.get('sort_by', 'id')
    sort_order = request.args.get('sort_order', 'asc')
    
    # Validate parameters
    if page < 1:
        abort(400)
    
    valid_sort_fields = ['id', 'name', 'retail_price', 'cost', 'brand', 'category']
    if sort_by not in valid_sort_fields:
        sort_by = 'id'
    
    if sort_order not in ['asc', 'desc']:
        sort_order = 'asc'
    
    conn = get_db_connection()
    if not conn:
        abort(500)
    
    try:
        cursor = conn.cursor()
        
        # First, verify department exists
        cursor.execute("SELECT name FROM departments WHERE id = ?", (department_id,))
        dept_result = cursor.fetchone()
        
        if dept_result is None:
            conn.close()
            return jsonify({
                'error': 'Department not found',
                'message': f'Department with ID {department_id} does not exist',
                'department_id': department_id
            }), 404
        
        department_name = dept_result[0]
        
        # Build the query with department filter
        where_conditions = ["p.department_id = ?"]
        params = [department_id]
        
        if category:
            where_conditions.append("p.category = ?")
            params.append(category)
        
        if brand:
            where_conditions.append("p.brand = ?")
            params.append(brand)
        
        if min_price is not None:
            where_conditions.append("p.retail_price >= ?")
            params.append(min_price)
        
        if max_price is not None:
            where_conditions.append("p.retail_price <= ?")
            params.append(max_price)
        
        if search:
            where_conditions.append("p.name LIKE ?")
            params.append(f"%{search}%")
        
        where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # Count total records for pagination
        count_query = f"""
            SELECT COUNT(*) 
            FROM products p
            JOIN departments d ON p.department_id = d.id
            {where_clause}
        """
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]
        
        # Calculate pagination info
        total_pages = math.ceil(total_count / limit)
        offset = (page - 1) * limit
        
        # Build main query
        query = f"""
            SELECT p.id, p.cost, p.category, p.name, p.brand, p.retail_price, 
                   p.department, p.sku, p.distribution_center_id, p.created_at,
                   d.name as department_name, d.description as department_description
            FROM products p
            JOIN departments d ON p.department_id = d.id
            {where_clause}
            ORDER BY p.{sort_by} {sort_order.upper()}
            LIMIT ? OFFSET ?
        """
        
        params.extend([limit, offset])
        cursor.execute(query, params)
        products = cursor.fetchall()
        
        # Convert to list of dictionaries
        products_list = [dict_from_row(product) for product in products]
        
        conn.close()
        
        # Build response
        response = {
            'department_id': department_id,
            'department_name': department_name,
            'products': products_list,
            'pagination': {
                'page': page,
                'limit': limit,
                'total_count': total_count,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1,
                'next_page': page + 1 if page < total_pages else None,
                'prev_page': page - 1 if page > 1 else None
            },
            'filters': {
                'category': category,
                'brand': brand,
                'min_price': min_price,
                'max_price': max_price,
                'search': search,
                'sort_by': sort_by,
                'sort_order': sort_order
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except sqlite3.Error as e:
        logger.error(f"Database error in get_department_products: {e}")
        conn.close()
        abort(500)
    except Exception as e:
        logger.error(f"Error in get_department_products: {e}")
        conn.close()
        abort(500)

if __name__ == '__main__':
    print("=" * 60)
    print("           PRODUCTS REST API")
    print("=" * 60)
    print("API Endpoints:")
    print("  GET /                     - API information")
    print("  GET /health               - Health check")
    print("  GET /api/products         - List all products (with pagination)")
    print("  GET /api/products/{id}    - Get specific product by ID")
    print("  GET /api/products/stats   - Get product statistics")
    print("=" * 60)
    print("Starting server on http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
