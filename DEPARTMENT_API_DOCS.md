# Department API Endpoints Documentation

## Overview
This document describes the new department-related API endpoints that have been added to the e-commerce REST API. These endpoints provide comprehensive access to department data and department-based product filtering.

## Base URL
```
http://localhost:5000/api
```

## Endpoints

### 1. List All Departments
**GET** `/api/departments`

Returns a list of all departments with their product counts and basic statistics.

**Response Example:**
```json
{
  "departments": [
    {
      "id": 2,
      "name": "Women",
      "description": "Women's clothing and accessories",
      "created_at": "2025-07-31 05:57:33",
      "product_count": 15989,
      "avg_price": 55.94,
      "min_price": 0.02,
      "max_price": 903.0
    },
    {
      "id": 1,
      "name": "Men",
      "description": "Men's clothing and accessories",
      "created_at": "2025-07-31 05:57:33",
      "product_count": 13131,
      "avg_price": 63.21,
      "min_price": 1.5,
      "max_price": 999.0
    }
  ],
  "total_departments": 2,
  "timestamp": "2025-07-31T11:52:59.892046"
}
```

### 2. Get Department Details
**GET** `/api/departments/{id}`

Returns detailed information about a specific department including top categories and brands.

**Parameters:**
- `id` (path, required): Department ID

**Response Example:**
```json
{
  "department": {
    "id": 1,
    "name": "Men",
    "description": "Men's clothing and accessories",
    "created_at": "2025-07-31 05:57:33",
    "product_count": 13131,
    "avg_price": 63.21,
    "min_price": 1.5,
    "max_price": 999.0,
    "avg_cost": 30.46,
    "top_categories": [
      {
        "category": "Jeans",
        "count": 1117,
        "avg_price": 101.16
      },
      {
        "category": "Underwear",
        "count": 1088,
        "avg_price": 27.16
      }
    ],
    "top_brands": [
      {
        "brand": "Calvin Klein",
        "count": 314,
        "avg_price": 61.50
      },
      {
        "brand": "Carhartt",
        "count": 289,
        "avg_price": 72.49
      }
    ]
  },
  "timestamp": "2025-07-31T11:53:08.275778"
}
```

**Error Response (404):**
```json
{
  "error": "Department not found",
  "message": "Department with ID 999 does not exist",
  "department_id": 999
}
```

### 3. Get Products by Department
**GET** `/api/departments/{id}/products`

Returns all products in a specific department with comprehensive filtering and pagination.

**Parameters:**
- `id` (path, required): Department ID
- `page` (query, optional): Page number (default: 1)
- `limit` (query, optional): Items per page (default: 20, max: 100)
- `category` (query, optional): Filter by category within the department
- `brand` (query, optional): Filter by brand within the department
- `min_price` (query, optional): Minimum retail price
- `max_price` (query, optional): Maximum retail price
- `search` (query, optional): Search in product name
- `sort_by` (query, optional): Sort by field (id, name, retail_price, cost, brand, category)
- `sort_order` (query, optional): Sort order (asc, desc)

**Example Requests:**
```
GET /api/departments/1/products?limit=5
GET /api/departments/1/products?category=Jeans&limit=10
GET /api/departments/1/products?min_price=50&max_price=100
GET /api/departments/1/products?search=Calvin&brand=Calvin Klein
GET /api/departments/1/products?sort_by=retail_price&sort_order=desc
```

**Response Example:**
```json
{
  "department_id": 1,
  "department_name": "Men",
  "products": [
    {
      "id": 15990,
      "name": "Hurley Men's One and Only Premium Raglan Long Sleeve",
      "brand": "Hurley",
      "category": "Tops & Tees",
      "retail_price": 32.0,
      "cost": 18.53,
      "department": "Men",
      "department_name": "Men",
      "department_description": "Men's clothing and accessories",
      "sku": "0852B1445F41F52E5B5008896B0A1F570",
      "distribution_center_id": 1,
      "created_at": "2025-07-31 05:57:12"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total_count": 13131,
    "total_pages": 657,
    "has_next": true,
    "has_prev": false,
    "next_page": 2,
    "prev_page": null
  },
  "filters": {
    "category": null,
    "brand": null,
    "min_price": null,
    "max_price": null,
    "search": null,
    "sort_by": "id",
    "sort_order": "asc"
  },
  "timestamp": "2025-07-31T11:53:16.652157"
}
```

**Error Response (404):**
```json
{
  "error": "Department not found",
  "message": "Department with ID 999 does not exist",
  "department_id": 999
}
```

## Features

### Database Queries
- All endpoints use SQL JOIN operations between `products` and `departments` tables
- Efficient querying with proper indexing on foreign keys
- Aggregation functions for statistics (COUNT, AVG, MIN, MAX)

### Error Handling
- **400 Bad Request**: Invalid parameters (e.g., negative department ID)
- **404 Not Found**: Department doesn't exist
- **500 Internal Server Error**: Database or server errors
- All errors return structured JSON responses

### Filtering & Search
- **Category filtering**: Filter products by category within department
- **Brand filtering**: Filter products by brand within department
- **Price range**: Filter by minimum and maximum retail price
- **Text search**: Search in product names (case-insensitive, partial matching)
- **Sorting**: Sort by multiple fields in ascending or descending order

### Pagination
- Configurable page size (max 100 items per page)
- Complete pagination metadata (total pages, current page, has next/prev)
- Direct links to next/previous pages

### Data Enrichment
- Products include both original `department` field and joined `department_name`/`department_description`
- Department details include top categories and brands with statistics
- All responses include timestamps for cache management

## Database Schema
The endpoints work with the normalized database structure:

**departments table:**
- `id` (PRIMARY KEY)
- `name`
- `description`
- `created_at`

**products table:**
- `id` (PRIMARY KEY)
- `department_id` (FOREIGN KEY → departments.id)
- `name`, `brand`, `category`, `retail_price`, `cost`, etc.

## Testing
A comprehensive test suite is available in `test_department_endpoints.py` that covers:
- Basic functionality of all endpoints
- Error handling (404 responses)
- Filtering and search functionality
- Pagination behavior
- Data validation

Run tests with:
```bash
python test_department_endpoints.py
```

## Performance Considerations
- Queries are optimized with proper JOIN operations
- Pagination prevents large result sets
- Database indexing on `department_id` foreign key
- Limited result sets with configurable limits
- Efficient aggregation queries for statistics
