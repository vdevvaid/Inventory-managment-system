// Search functionality
document.getElementById('searchInput').addEventListener('keyup', function() {
    const searchText = this.value.toLowerCase();
    const items = document.querySelectorAll('.inventory-item');
    
    items.forEach(item => {
        const itemName = item.querySelector('h4').textContent.toLowerCase();
        const itemDesc = item.querySelector('p:last-child').textContent.toLowerCase();
        
        if (itemName.includes(searchText) || itemDesc.includes(searchText)) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
});

// Sort functionality
document.getElementById('sortSelect').addEventListener('change', function() {
    const sortBy = this.value;
    const itemsContainer = document.querySelector('.row');
    const items = Array.from(document.querySelectorAll('.col-md-6'));
    
    items.sort((a, b) => {
        if (sortBy === 'name') {
            const nameA = a.querySelector('h4').textContent.toLowerCase();
            const nameB = b.querySelector('h4').textContent.toLowerCase();
            return nameA.localeCompare(nameB);
        } else {
            const qtyA = parseInt(a.querySelector('p').textContent.split(':')[1]);
            const qtyB = parseInt(b.querySelector('p').textContent.split(':')[1]);
            return qtyB - qtyA;
        }
    });
    
    items.forEach(item => itemsContainer.appendChild(item));
});

// Add loading states
function showLoading(button) {
    const originalText = button.innerHTML;
    button.setAttribute('data-original-text', originalText);
    button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
    button.disabled = true;
}

function hideLoading(button) {
    const originalText = button.getAttribute('data-original-text');
    button.innerHTML = originalText;
    button.disabled = false;
}

// Form submission with loading state
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function(e) {
        const submitButton = this.querySelector('button[type="submit"]');
        showLoading(submitButton);
    });
});

// Add custom notifications
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `custom-notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
} 