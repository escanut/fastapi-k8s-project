// We use a relative path here to ensure it works in both development and production environments
const API_URL = '/api';

// Check API health on page load
async function checkHealth() {
    const statusDiv = document.getElementById('health-status');
    try {
        const response = await fetch(`${API_URL}/health`);
        const data = await response.json();
        
        if (data.status === 'healthy') {
            statusDiv.className = 'health-status healthy';
            statusDiv.textContent = '✓ API Connected - Database Online';
        } else {
            statusDiv.className = 'health-status unhealthy';
            statusDiv.textContent = '✗ API Error - Check Backend';
        }
    } catch (error) {
        statusDiv.className = 'health-status unhealthy';
        statusDiv.textContent = '✗ Cannot Connect to API';
    }
}

// Load all products
async function loadProducts() {
    const productsList = document.getElementById('products-list');
    productsList.innerHTML = '<div class="loading">Loading products...</div>';
    
    try {
        // Changed from /api/products to /products
        const response = await fetch(`${API_URL}/products`);
        const products = await response.json();
        
        if (products.length === 0) {
            productsList.innerHTML = '<p>No products yet. Add one above!</p>';
            return;
        }
        
        productsList.innerHTML = products.map(product => `
            <div class="product-card">
                <button class="delete-btn" onclick="deleteProduct(${product.id})">Delete</button>
                <h3>${product.name}</h3>
                <p>${product.description || 'No description'}</p>
                <p class="price">$${parseFloat(product.price).toFixed(2)}</p>
                <p style="font-size: 12px; color: #999;">
                    Added: ${new Date(product.created_at).toLocaleDateString()}
                </p>
            </div>
        `).join('');
        
    } catch (error) {
        productsList.innerHTML = '<div class="error">Failed to load products</div>';
    }
}

// Delete product function
async function deleteProduct(productId) {
    if (!confirm('Are you sure you want to delete this product?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/products/${productId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            // Reload products after successful deletion
            loadProducts();
        } else {
            const error = await response.json();
            alert('Failed to delete product: ' + (error.detail || 'Unknown error'));
        }
    } catch (error) {
        alert('Error deleting product: ' + error.message);
    }
}

// Handle form submission
document.getElementById('product-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const name = document.getElementById('name').value;
    const description = document.getElementById('description').value;
    const price = document.getElementById('price').value;
    
    try {
        // Changed from /api/products to /products
        const response = await fetch(`${API_URL}/products`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                description: description,
                price: parseFloat(price)
            })
        });
        
        if (response.ok) {
            // Clear form
            document.getElementById('product-form').reset();
            // Reload products
            loadProducts();
        } else {
            const error = await response.json();
            alert('Failed to add product: ' + (error.detail || 'Unknown error'));
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
});

// Load data on page load
checkHealth();
loadProducts();