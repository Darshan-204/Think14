# Products REST API Documentation

## Overview
This REST API provides access to the e-commerce products database. It supports retrieving product information with pagination, filtering, sorting, and search capabilities.

## Base URL
```
http://localhost:5000
```

## Endpoints

### 1. API Information
**GET /** 
- **Description**: Welcome endpoint with API information
- **Response**: JSON with API version and available endpoints

### 2. Health Check
**GET /health**
- **Description**: Check API and database health
- **Response**: JSON with status and database connectivity

### 3. List Products
**GET /api/products**
- **Description**: Retrieve a list of products with pagination and filtering
- **Query Parameters**:
  - `page` (integer): Page number (default: 1)
  - `limit` (integer): Items per page (default: 20, max: 100)
  - `category` (string): Filter by product category
  - `department` (string): Filter by department (Men/Women)
  - `brand` (string): Filter by brand name
  - `min_price` (float): Minimum retail price
  - `max_price` (float): Maximum retail price
  - `search` (string): Search in product names
  - `sort_by` (string): Sort by field (id, name, retail_price, cost, brand, category)
  - `sort_order` (string): Sort order (asc, desc)

**Example Requests**:
```
GET /api/products
GET /api/products?page=2&limit=10
GET /api/products?department=Women&category=Jeans
GET /api/products?min_price=50&max_price=100
GET /api/products?search=Calvin&sort_by=retail_price&sort_order=desc
```

**Response Format**:
```json
{
  "products": [
    {
      "id": 1,
      "cost": 27.05,
      "category": "Tops & Tees",
      "name": "Product Name",
      "brand": "Brand Name",
      "retail_price": 49.00,
      "department": "Women",
      "sku": "UNIQUE_SKU",
      "distribution_center_id": 1,
      "created_at": "2025-07-31 04:30:58"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total_count": 29120,
    "total_pages": 1456,
    "has_next": true,
    "has_prev": false,
    "next_page": 2,
    "prev_page": null
  },
  "filters": {
    "category": null,
    "department": null,
    "brand": null,
    "min_price": null,
    "max_price": null,
    "search": null,
    "sort_by": "id",
    "sort_order": "asc"
  }
}
```

### 4. Get Product by ID
**GET /api/products/{id}**
- **Description**: Retrieve a specific product by its ID
- **Parameters**:
  - `id` (integer): Product ID
- **Response**: JSON with product details or 404 if not found

**Example Requests**:
```
GET /api/products/1
GET /api/products/12345
```

**Response Format** (Success):
```json
{
  "product": {
    "id": 1,
    "cost": 27.05,
    "category": "Tops & Tees",
    "name": "Product Name",
    "brand": "Brand Name",
    "retail_price": 49.00,
    "department": "Women",
    "sku": "UNIQUE_SKU",
    "distribution_center_id": 1,
    "created_at": "2025-07-31 04:30:58"
  }
}
```

**Response Format** (Not Found):
```json
{
  "error": "Product not found",
  "message": "Product with ID 999999 does not exist",
  "product_id": 999999
}
```

### 5. Product Statistics
**GET /api/products/stats**
- **Description**: Get comprehensive statistics about the product database
- **Response**: JSON with various statistics

**Response Format**:
```json
{
  "overall": {
    "total_products": 29120,
    "min_price": 0.02,
    "max_price": 999.00,
    "avg_price": 59.22,
    "min_cost": 0.01,
    "max_cost": 557.15,
    "avg_cost": 28.48
  },
  "by_department": [
    {
      "department": "Men",
      "count": 13131,
      "avg_price": 63.21
    },
    {
      "department": "Women", 
      "count": 15989,
      "avg_price": 55.94
    }
  ],
  "top_categories": [...],
  "top_brands": [...],
  "distribution_centers": [...]
}
```

## Error Handling

The API returns appropriate HTTP status codes:

- **200**: Success
- **400**: Bad Request (invalid parameters)
- **404**: Not Found (resource doesn't exist)
- **500**: Internal Server Error

Error responses include descriptive messages:
```json
{
  "error": "Error Type",
  "message": "Descriptive error message",
  "status_code": 400
}
```

## Database Schema

The products table has the following structure:
- `id` (INTEGER PRIMARY KEY): Unique product identifier
- `cost` (REAL): Product cost price
- `category` (TEXT): Product category
- `name` (TEXT): Product name
- `brand` (TEXT): Brand name
- `retail_price` (REAL): Retail price
- `department` (TEXT): Department (Men/Women)
- `sku` (TEXT UNIQUE): Stock Keeping Unit
- `distribution_center_id` (INTEGER): Distribution center ID
- `created_at` (DATETIME): Record creation timestamp

## Running the API

1. Ensure the database file `ecommerce.db` exists
2. Install dependencies: `pip install flask`
3. Run the server: `python products_api.py`
4. Access the API at `http://localhost:5000`

## Testing

Use the provided test script to verify all endpoints:
```bash
python test_api.py
```

This will test all endpoints and display formatted responses.
