// E-Commerce Products Frontend Application
// API Configuration
const API_BASE_URL = 'http://localhost:5000';

// Global variables
let currentPage = 1;
let totalPages = 1;
let currentFilters = {};
let allCategories = [];
let allDepartments = [];
let currentDepartment = null;
let currentDepartmentPage = 1;
let departmentTotalPages = 1;
let currentDepartmentCategory = '';

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadDepartments();
    loadCategories();
    loadProducts(1);
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // Search input with debounce
    let searchTimeout;
    document.getElementById('searchInput').addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            loadProducts(1);
        }, 500);
    });

    // Filter change events
    ['departmentFilter', 'categoryFilter', 'sortBy', 'sortOrder', 'minPrice', 'maxPrice'].forEach(id => {
        document.getElementById(id).addEventListener('change', () => {
            loadProducts(1);
        });
    });

    // Enter key on price inputs
    ['minPrice', 'maxPrice'].forEach(id => {
        document.getElementById(id).addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                loadProducts(1);
            }
        });
    });

    // Department page event listeners
    setupDepartmentEventListeners();
}

// Setup department-specific event listeners
function setupDepartmentEventListeners() {
    // Department search input with debounce
    let deptSearchTimeout;
    const deptSearchInput = document.getElementById('deptSearchInput');
    if (deptSearchInput) {
        deptSearchInput.addEventListener('input', function() {
            clearTimeout(deptSearchTimeout);
            deptSearchTimeout = setTimeout(() => {
                if (currentDepartment) {
                    loadDepartmentProducts(currentDepartment.id, 1);
                }
            }, 500);
        });
    }

    // Department filter change events
    ['deptBrandFilter', 'deptSortBy', 'deptSortOrder', 'deptMinPrice', 'deptMaxPrice'].forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('change', () => {
                if (currentDepartment) {
                    loadDepartmentProducts(currentDepartment.id, 1);
                }
            });
        }
    });

    // Enter key on department price inputs
    ['deptMinPrice', 'deptMaxPrice'].forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && currentDepartment) {
                    loadDepartmentProducts(currentDepartment.id, 1);
                }
            });
        }
    });
}

// Load categories for filter dropdown
async function loadCategories() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/products/stats`);
        const data = await response.json();
        
        if (data.top_categories) {
            allCategories = data.top_categories;
            populateCategoryFilter();
        }
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

// Load departments
async function loadDepartments() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/departments`);
        const data = await response.json();
        
        if (response.ok && data.departments) {
            allDepartments = data.departments;
            populateDepartmentNavigation();
        }
    } catch (error) {
        console.error('Error loading departments:', error);
    }
}

// Populate department navigation dropdown
function populateDepartmentNavigation() {
    const departmentsList = document.getElementById('departmentsList');
    
    // Keep the "All Departments" item and divider
    const existingItems = departmentsList.innerHTML;
    
    // Add department items
    allDepartments.forEach(department => {
        const listItem = document.createElement('li');
        const icon = department.name === 'Men' ? 'fas fa-male' : 'fas fa-female';
        
        listItem.innerHTML = `
            <a class="dropdown-item" href="#" onclick="showDepartmentPage(${department.id})">
                <i class="${icon}"></i> ${department.name} 
                <span class="badge bg-secondary ms-2">${department.product_count}</span>
            </a>
        `;
        
        departmentsList.appendChild(listItem);
    });
}

// Populate category filter dropdown
function populateCategoryFilter() {
    const categorySelect = document.getElementById('categoryFilter');
    categorySelect.innerHTML = '<option value="">All Categories</option>';
    
    allCategories.forEach(category => {
        const option = document.createElement('option');
        option.value = category.category;
        option.textContent = `${category.category} (${category.count})`;
        categorySelect.appendChild(option);
    });
}

// Load products with filters and pagination
async function loadProducts(page = 1) {
    showLoading('productsContainer');
    
    try {
        const filters = getFilters();
        const queryParams = new URLSearchParams({
            page: page,
            limit: 12,
            ...filters
        });

        const response = await fetch(`${API_BASE_URL}/api/products?${queryParams}`);
        const data = await response.json();

        if (response.ok) {
            currentPage = page;
            totalPages = data.pagination.total_pages;
            currentFilters = filters;
            
            displayProducts(data.products);
            updatePagination(data.pagination);
        } else {
            showError('Failed to load products: ' + data.message);
        }
    } catch (error) {
        console.error('Error loading products:', error);
        showError('Failed to connect to the server. Please ensure the API is running.');
    }
}

// Get current filter values
function getFilters() {
    const filters = {};
    
    const search = document.getElementById('searchInput').value.trim();
    if (search) filters.search = search;
    
    const department = document.getElementById('departmentFilter').value;
    if (department) filters.department = department;
    
    const category = document.getElementById('categoryFilter').value;
    if (category) filters.category = category;
    
    const minPrice = document.getElementById('minPrice').value;
    if (minPrice) filters.min_price = minPrice;
    
    const maxPrice = document.getElementById('maxPrice').value;
    if (maxPrice) filters.max_price = maxPrice;
    
    filters.sort_by = document.getElementById('sortBy').value;
    filters.sort_order = document.getElementById('sortOrder').value;
    
    return filters;
}

// Display products in grid format
function displayProducts(products) {
    const container = document.getElementById('productsContainer');
    
    if (products.length === 0) {
        container.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-search fa-3x text-muted mb-3"></i>
                <h4>No products found</h4>
                <p class="text-muted">Try adjusting your search criteria or filters.</p>
            </div>
        `;
        return;
    }
    
    const productsHTML = products.map(product => createProductCard(product)).join('');
    container.innerHTML = `<div class="row">${productsHTML}</div>`;
}

// Create individual product card
function createProductCard(product) {
    const profitMargin = ((product.retail_price - product.cost) / product.cost * 100).toFixed(1);
    
    return `
        <div class="col-lg-4 col-md-6 mb-4">
            <div class="card product-card h-100" onclick="showProductDetail(${product.id})">
                <div class="product-image-placeholder">
                    <i class="fas fa-tshirt"></i>
                </div>
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <span class="product-category">${product.category}</span>
                        <span class="product-department">${product.department}</span>
                    </div>
                    <h5 class="card-title">${truncateText(product.name, 60)}</h5>
                    <p class="card-text">
                        <strong>Brand:</strong> ${product.brand}<br>
                        <strong>SKU:</strong> ${product.sku.substring(0, 12)}...
                    </p>
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <div class="product-price">$${product.retail_price.toFixed(2)}</div>
                            <div class="product-cost">Cost: $${product.cost.toFixed(2)}</div>
                        </div>
                        <div class="text-end">
                            <small class="text-success">+${profitMargin}% margin</small>
                        </div>
                    </div>
                </div>
                <div class="card-footer bg-transparent">
                    <button class="btn btn-primary btn-sm w-100" onclick="event.stopPropagation(); showProductDetail(${product.id})">
                        <i class="fas fa-eye"></i> View Details
                    </button>
                </div>
            </div>
        </div>
    `;
}

// Show product detail modal
async function showProductDetail(productId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/products/${productId}`);
        const data = await response.json();
        
        if (response.ok) {
            displayProductDetail(data.product);
            const modal = new bootstrap.Modal(document.getElementById('productDetailModal'));
            modal.show();
        } else {
            showError('Product not found: ' + data.message);
        }
    } catch (error) {
        console.error('Error loading product detail:', error);
        showError('Failed to load product details.');
    }
}

// Display product detail in modal
function displayProductDetail(product) {
    const profitMargin = ((product.retail_price - product.cost) / product.cost * 100).toFixed(1);
    const profitAmount = (product.retail_price - product.cost).toFixed(2);
    
    const detailHTML = `
        <div class="row">
            <div class="col-md-4">
                <div class="product-image-placeholder mb-3" style="height: 250px;">
                    <i class="fas fa-tshirt fa-4x"></i>
                </div>
                <div class="text-center">
                    <span class="product-category">${product.category}</span>
                    <span class="product-department ms-2">${product.department}</span>
                </div>
            </div>
            <div class="col-md-8">
                <h3>${product.name}</h3>
                <p class="text-muted mb-3">by ${product.brand}</p>
                
                <div class="row mb-3">
                    <div class="col-6">
                        <h4 class="product-price mb-0">$${product.retail_price.toFixed(2)}</h4>
                        <small class="text-muted">Retail Price</small>
                    </div>
                    <div class="col-6">
                        <h5 class="text-muted mb-0">$${product.cost.toFixed(2)}</h5>
                        <small class="text-muted">Cost Price</small>
                    </div>
                </div>
                
                <div class="alert alert-success">
                    <strong>Profit:</strong> $${profitAmount} (${profitMargin}% margin)
                </div>
                
                <table class="table table-borderless">
                    <tr>
                        <td><strong>Product ID:</strong></td>
                        <td>${product.id}</td>
                    </tr>
                    <tr>
                        <td><strong>SKU:</strong></td>
                        <td><code>${product.sku}</code></td>
                    </tr>
                    <tr>
                        <td><strong>Category:</strong></td>
                        <td>${product.category}</td>
                    </tr>
                    <tr>
                        <td><strong>Department:</strong></td>
                        <td>${product.department}</td>
                    </tr>
                    <tr>
                        <td><strong>Distribution Center:</strong></td>
                        <td>Center ${product.distribution_center_id}</td>
                    </tr>
                    <tr>
                        <td><strong>Added:</strong></td>
                        <td>${formatDate(product.created_at)}</td>
                    </tr>
                </table>
            </div>
        </div>
    `;
    
    document.getElementById('productDetailBody').innerHTML = detailHTML;
    document.getElementById('productDetailModalLabel').textContent = truncateText(product.name, 50);
}

// Update pagination controls
function updatePagination(pagination) {
    const paginationContainer = document.getElementById('pagination');
    
    if (pagination.total_pages <= 1) {
        paginationContainer.innerHTML = '';
        return;
    }
    
    let paginationHTML = '';
    
    // Previous button
    if (pagination.has_prev) {
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="loadProducts(${pagination.prev_page})">
                    <i class="fas fa-chevron-left"></i>
                </a>
            </li>
        `;
    }
    
    // Page numbers
    const startPage = Math.max(1, pagination.page - 2);
    const endPage = Math.min(pagination.total_pages, pagination.page + 2);
    
    if (startPage > 1) {
        paginationHTML += `<li class="page-item"><a class="page-link" href="#" onclick="loadProducts(1)">1</a></li>`;
        if (startPage > 2) {
            paginationHTML += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
        }
    }
    
    for (let i = startPage; i <= endPage; i++) {
        paginationHTML += `
            <li class="page-item ${i === pagination.page ? 'active' : ''}">
                <a class="page-link" href="#" onclick="loadProducts(${i})">${i}</a>
            </li>
        `;
    }
    
    if (endPage < pagination.total_pages) {
        if (endPage < pagination.total_pages - 1) {
            paginationHTML += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
        }
        paginationHTML += `<li class="page-item"><a class="page-link" href="#" onclick="loadProducts(${pagination.total_pages})">${pagination.total_pages}</a></li>`;
    }
    
    // Next button
    if (pagination.has_next) {
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="loadProducts(${pagination.next_page})">
                    <i class="fas fa-chevron-right"></i>
                </a>
            </li>
        `;
    }
    
    paginationContainer.innerHTML = paginationHTML;
}

// View switching functions
function showProductList() {
    hideAllViews();
    document.getElementById('productListView').style.display = 'block';
    loadProducts(1);
}

function showDepartmentList() {
    hideAllViews();
    document.getElementById('departmentListView').style.display = 'block';
    loadDepartmentList();
}

function showDepartmentPage(departmentId) {
    hideAllViews();
    document.getElementById('departmentPageView').style.display = 'block';
    loadDepartmentDetails(departmentId);
}

function hideAllViews() {
    document.getElementById('productListView').style.display = 'none';
    document.getElementById('departmentListView').style.display = 'none';
    document.getElementById('departmentPageView').style.display = 'none';
    document.getElementById('statsView').style.display = 'none';
}

// Load and display department list
async function loadDepartmentList() {
    showLoading('departmentsContainer');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/departments`);
        const data = await response.json();
        
        if (response.ok) {
            displayDepartments(data.departments);
        } else {
            showError('Failed to load departments: ' + data.message);
        }
    } catch (error) {
        console.error('Error loading departments:', error);
        showError('Failed to load departments.');
    }
}

// Display departments
function displayDepartments(departments) {
    const container = document.getElementById('departmentsContainer');
    
    if (departments.length === 0) {
        container.innerHTML = '<div class="text-center py-5"><h4>No departments found</h4></div>';
        return;
    }
    
    let departmentsHTML = '<div class="row">';
    
    departments.forEach(department => {
        const icon = department.name === 'Men' ? 'fas fa-male' : 'fas fa-female';
        
        departmentsHTML += `
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="department-card" onclick="showDepartmentPage(${department.id})">
                    <div class="department-header">
                        <div class="department-icon">
                            <i class="${icon}"></i>
                        </div>
                        <h4>${department.name}</h4>
                        <p class="mb-0">${department.description}</p>
                    </div>
                    <div class="department-stats">
                        <div class="stat-item">
                            <div class="stat-number">${department.product_count.toLocaleString()}</div>
                            <div class="stat-label">Products</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number">$${department.avg_price.toFixed(2)}</div>
                            <div class="stat-label">Avg Price</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number">$${department.min_price.toFixed(2)}</div>
                            <div class="stat-label">Min Price</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number">$${department.max_price.toFixed(2)}</div>
                            <div class="stat-label">Max Price</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    departmentsHTML += '</div>';
    container.innerHTML = departmentsHTML;
}

// Load department details and products
async function loadDepartmentDetails(departmentId) {
    try {
        // Load department details
        const deptResponse = await fetch(`${API_BASE_URL}/api/departments/${departmentId}`);
        const deptData = await deptResponse.json();
        
        if (deptResponse.ok) {
            currentDepartment = deptData.department;
            displayDepartmentHeader(currentDepartment);
            setupDepartmentCategoryFilter(currentDepartment);
            loadDepartmentProducts(departmentId, 1);
        } else {
            showError('Department not found: ' + deptData.message);
        }
    } catch (error) {
        console.error('Error loading department details:', error);
        showError('Failed to load department details.');
    }
}

// Display department header
function displayDepartmentHeader(department) {
    const icon = department.name === 'Men' ? 'fas fa-male' : 'fas fa-female';
    
    document.getElementById('departmentPageTitle').innerHTML = `
        <i class="${icon}"></i> ${department.name}
    `;
    document.getElementById('departmentPageDescription').textContent = department.description;
    document.getElementById('currentDepartmentBreadcrumb').textContent = department.name;
    document.getElementById('departmentProductCount').textContent = department.product_count.toLocaleString();
    document.getElementById('departmentAvgPrice').textContent = `$${department.avg_price.toFixed(2)}`;
}

// Setup category filter pills for department
function setupDepartmentCategoryFilter(department) {
    const categoryPills = document.getElementById('categoryPills');
    
    let pillsHTML = `
        <a href="#" class="filter-pill active" onclick="filterDepartmentByCategory('')">
            All Categories (${department.product_count})
        </a>
    `;
    
    department.top_categories.forEach(category => {
        pillsHTML += `
            <a href="#" class="filter-pill" onclick="filterDepartmentByCategory('${category.category}')">
                ${category.category} (${category.count})
            </a>
        `;
    });
    
    categoryPills.innerHTML = pillsHTML;
}

// Filter department by category
function filterDepartmentByCategory(category) {
    // Update active pill
    document.querySelectorAll('.filter-pill').forEach(pill => {
        pill.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Set category filter and reload products
    if (currentDepartment) {
        // Update the category filter (we'll add this as a hidden input or data attribute)
        currentDepartmentCategory = category;
        loadDepartmentProducts(currentDepartment.id, 1);
    }
}

// Load department products
async function loadDepartmentProducts(departmentId, page = 1) {
    showLoading('departmentProductsContainer');
    
    try {
        const filters = getDepartmentFilters();
        const queryParams = new URLSearchParams({
            page: page,
            limit: 12,
            ...filters
        });

        const response = await fetch(`${API_BASE_URL}/api/departments/${departmentId}/products?${queryParams}`);
        const data = await response.json();

        if (response.ok) {
            currentDepartmentPage = page;
            departmentTotalPages = data.pagination.total_pages;
            
            displayDepartmentProducts(data.products);
            updateDepartmentPagination(data.pagination);
        } else {
            showError('Failed to load department products: ' + data.message);
        }
    } catch (error) {
        console.error('Error loading department products:', error);
        showError('Failed to load department products.');
    }
}

// Get department filters
function getDepartmentFilters() {
    const filters = {};
    
    const search = document.getElementById('deptSearchInput')?.value?.trim();
    const brand = document.getElementById('deptBrandFilter')?.value;
    const minPrice = document.getElementById('deptMinPrice')?.value;
    const maxPrice = document.getElementById('deptMaxPrice')?.value;
    const sortBy = document.getElementById('deptSortBy')?.value || 'id';
    const sortOrder = document.getElementById('deptSortOrder')?.value || 'asc';
    
    if (search) filters.search = search;
    if (brand) filters.brand = brand;
    if (minPrice) filters.min_price = minPrice;
    if (maxPrice) filters.max_price = maxPrice;
    if (currentDepartmentCategory) filters.category = currentDepartmentCategory;
    
    filters.sort_by = sortBy;
    filters.sort_order = sortOrder;
    
    return filters;
}

// Display department products
function displayDepartmentProducts(products) {
    const container = document.getElementById('departmentProductsContainer');
    
    if (products.length === 0) {
        container.innerHTML = '<div class="text-center py-5"><h4>No products found</h4></div>';
        return;
    }
    
    let productsHTML = '<div class="row">';
    
    products.forEach(product => {
        productsHTML += `
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="product-card">
                    <div class="product-image-placeholder">
                        <i class="fas fa-image"></i>
                    </div>
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <span class="product-category">${product.category}</span>
                            <span class="product-department">${product.department_name}</span>
                        </div>
                        <h6 class="card-title">${truncateText(product.name, 60)}</h6>
                        <p class="text-muted mb-2">
                            <i class="fas fa-tag"></i> ${product.brand}
                        </p>
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <span class="product-price">$${product.retail_price}</span>
                                <br>
                                <small class="product-cost">Cost: $${product.cost}</small>
                            </div>
                            <button class="btn btn-primary btn-sm" onclick="showProductDetail(${product.id})">
                                <i class="fas fa-eye"></i> View
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    productsHTML += '</div>';
    container.innerHTML = productsHTML;
}

// Update department pagination
function updateDepartmentPagination(pagination) {
    const paginationContainer = document.getElementById('departmentPagination');
    
    if (pagination.total_pages <= 1) {
        document.getElementById('departmentPaginationNav').style.display = 'none';
        return;
    }
    
    document.getElementById('departmentPaginationNav').style.display = 'block';
    
    let paginationHTML = '';
    
    // Previous button
    if (pagination.has_prev) {
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="loadDepartmentProducts(${currentDepartment.id}, ${pagination.prev_page})">
                    <i class="fas fa-chevron-left"></i> Previous
                </a>
            </li>
        `;
    }
    
    // Page numbers
    const startPage = Math.max(1, pagination.page - 2);
    const endPage = Math.min(pagination.total_pages, pagination.page + 2);
    
    if (startPage > 1) {
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="loadDepartmentProducts(${currentDepartment.id}, 1)">1</a>
            </li>
        `;
        if (startPage > 2) {
            paginationHTML += '<li class="page-item disabled"><span class="page-link">...</span></li>';
        }
    }
    
    for (let i = startPage; i <= endPage; i++) {
        const activeClass = i === pagination.page ? 'active' : '';
        paginationHTML += `
            <li class="page-item ${activeClass}">
                <a class="page-link" href="#" onclick="loadDepartmentProducts(${currentDepartment.id}, ${i})">${i}</a>
            </li>
        `;
    }
    
    if (endPage < pagination.total_pages) {
        if (endPage < pagination.total_pages - 1) {
            paginationHTML += '<li class="page-item disabled"><span class="page-link">...</span></li>';
        }
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="loadDepartmentProducts(${currentDepartment.id}, ${pagination.total_pages})">${pagination.total_pages}</a>
            </li>
        `;
    }
    
    // Next button
    if (pagination.has_next) {
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="loadDepartmentProducts(${currentDepartment.id}, ${pagination.next_page})">
                    Next <i class="fas fa-chevron-right"></i>
                </a>
            </li>
        `;
    }
    
    paginationContainer.innerHTML = paginationHTML;
}

// Show statistics view
async function showStats() {
    hideAllViews();
    document.getElementById('statsView').style.display = 'block';
    
    showLoading('statsContainer');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/products/stats`);
        const data = await response.json();
        
        if (response.ok) {
            displayStats(data);
        } else {
            showError('Failed to load statistics: ' + data.message);
        }
    } catch (error) {
        console.error('Error loading statistics:', error);
        showError('Failed to load statistics.');
    }
}

// Display statistics
function displayStats(stats) {
    const statsHTML = `
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="stats-card">
                    <div class="stats-number">${stats.overall.total_products.toLocaleString()}</div>
                    <div class="text-muted">Total Products</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stats-card">
                    <div class="stats-number">$${stats.overall.avg_price.toFixed(2)}</div>
                    <div class="text-muted">Average Price</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stats-card">
                    <div class="stats-number">$${stats.overall.max_price.toFixed(2)}</div>
                    <div class="text-muted">Highest Price</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stats-card">
                    <div class="stats-number">$${stats.overall.min_price.toFixed(2)}</div>
                    <div class="text-muted">Lowest Price</div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-users"></i> By Department</h5>
                    </div>
                    <div class="card-body">
                        ${stats.by_department.map(dept => `
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <span>${dept.department}</span>
                                <span class="badge bg-primary">${dept.count.toLocaleString()} products</span>
                            </div>
                            <div class="progress mb-3" style="height: 6px;">
                                <div class="progress-bar" style="width: ${(dept.count / stats.overall.total_products * 100).toFixed(1)}%"></div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-tags"></i> Top Categories</h5>
                    </div>
                    <div class="card-body">
                        ${stats.top_categories.slice(0, 5).map((cat, index) => `
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <span>${cat.category}</span>
                                <span class="badge bg-secondary">${cat.count.toLocaleString()}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-star"></i> Top Brands</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            ${stats.top_brands.slice(0, 10).map(brand => `
                                <div class="col-md-6 mb-2">
                                    <div class="d-flex justify-content-between">
                                        <span>${brand.brand}</span>
                                        <span class="text-primary">${brand.count.toLocaleString()} products</span>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('statsContainer').innerHTML = statsHTML;
}

// Utility functions
function showLoading(containerId) {
    document.getElementById(containerId).innerHTML = `
        <div class="loading-spinner">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
    `;
}

function showError(message) {
    const errorHTML = `
        <div class="error-message">
            <i class="fas fa-exclamation-triangle"></i>
            <strong>Error:</strong> ${message}
        </div>
    `;
    
    document.getElementById('productsContainer').innerHTML = errorHTML;
}

function truncateText(text, length) {
    return text.length > length ? text.substring(0, length) + '...' : text;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}
