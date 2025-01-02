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

document.getElementById('newNoteForm').addEventListener('submit', function(e) {
    e.preventDefault(); // Prevenir el envío por defecto del formulario
    
    const formData = new FormData(this);
    
    fetch('/create_note', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message);
        alert('Nota creada exitosamente');
    })
    .catch(error => {
        console.error('Error al enviar el formulario:', error);
    });
});

document.addEventListener('DOMContentLoaded', () => {
    const toggleBlurBtn = document.getElementById('toggleBlurBtn');
    const moneyTexts = document.querySelectorAll('.blur-text');
    const eyeIcon = toggleBlurBtn.querySelector('i');

    let isBlurred = true;

    toggleBlurBtn.addEventListener('click', () => {
        moneyTexts.forEach((text) => {
            text.classList.toggle('blur-text');
        });

        if (isBlurred) {
            eyeIcon.classList.remove('fa-eye');
            eyeIcon.classList.add('fa-eye-slash');
        } else {
            eyeIcon.classList.remove('fa-eye-slash');
            eyeIcon.classList.add('fa-eye');
        }

        isBlurred = !isBlurred;
    });
});

