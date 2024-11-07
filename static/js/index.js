fetch('/api/order-stats')
    .then(response => response.json())
    .then(data => {
        document.getElementById('profitAmount').textContent = `$${data.profit.toFixed(2)}`;
        document.getElementById('pendingAmount').textContent = `$${data.pending.toFixed(2)}`;
        document.getElementById('investAmount').textContent = `$${data.invest.toFixed(2)}`;
    })
    .catch(error => console.error('Error al cargar los datos:', error));

document.getElementById('search').addEventListener('input', function() {
    const searchText = this.value.toLowerCase();
    const productContainer = document.getElementById('productContainer');
    const productContainers = document.querySelectorAll('.product-card-container');

    if (searchText.trim() !== "") {
        productContainer.style.display = "flex";
        productContainers.forEach(container => {
            const productName = container.querySelector('.card-title').textContent.toLowerCase();
            container.style.display = productName.includes(searchText) ? 'block' : 'none';
        });
    } else {
        productContainer.style.display = "none";
    }
});

document.getElementById('search').addEventListener('input', function() {
    const filter = this.value.toLowerCase();
    const products = document.querySelectorAll('.product-list-item');
    
    products.forEach(product => {
        const name = product.querySelector('.product-name').textContent.toLowerCase();
        product.style.display = name.includes(filter) ? 'flex' : 'none';
    });
});