document.addEventListener('DOMContentLoaded', () => {
    // Verificar que el botón y los elementos de fecha existen antes de agregar el event listener
    const filterDatesButton = document.getElementById('filterDatesButton');
    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');

    // Asegurarse de que el botón y los elementos de fecha existan antes de proceder
    if (filterDatesButton && startDateInput && endDateInput) {
        filterDatesButton.addEventListener('click', () => {
            const startDate = startDateInput.value;
            const endDate = endDateInput.value;

            // Verificar que se han proporcionado fechas
            const params = new URLSearchParams();
            if (startDate) params.append('startDate', startDate);
            if (endDate) params.append('endDate', endDate);

            // Realizar la solicitud con las fechas
            fetch(`/api/order-stats?${params.toString()}`)
                .then(response => response.json())
                .then(data => {
                    // Asegurarse de que los valores recibidos no sean nulos
                    const profit = data.profit || 0;
                    const pending = data.pending || 0;
                    const invest = data.invest || 0;

                    // Actualizar las cards con los datos recibidos
                    document.getElementById('profitAmount').textContent = `$${profit.toFixed(2)}`;
                    document.getElementById('pendingAmount').textContent = `$${pending.toFixed(2)}`;
                    document.getElementById('investAmount').textContent = `$${invest.toFixed(2)}`;
                })
                .catch(error => {
                    console.error('Error al cargar los datos con filtro de fechas:', error);
                });
        });
    } else {
        console.error('Faltan elementos en el DOM.');
    }

    // Cargar los datos iniciales cuando la página se carga
    fetch('/api/order-stats')
        .then(response => response.json())
        .then(data => {
            // Asegurarse de que los valores iniciales no sean nulos
            const profit = data.profit || 0;
            const pending = data.pending || 0;
            const invest = data.invest || 0;

            // Actualizar las cards con los datos iniciales
            document.getElementById('profitAmount').textContent = `$${profit.toFixed(2)}`;
            document.getElementById('pendingAmount').textContent = `$${pending.toFixed(2)}`;
            document.getElementById('investAmount').textContent = `$${invest.toFixed(2)}`;
        })
        .catch(error => {
            console.error('Error al cargar los datos iniciales:', error);
        });
});

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

function updateRepo() {
    fetch("/update_repo", { method: "POST" })
        .then(response => response.json())
        .then(data => alert(data.message))
        .catch(error => console.error("Error updating repo:", error));
}

document.getElementById('applyDateRange').addEventListener('click', function() {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;

    // Si alguna de las fechas no está seleccionada, mostrar un mensaje y salir
    if (!startDate || !endDate) {
        alert('Por favor, selecciona un rango de fechas.');
        return;
    }

    // Enviar las fechas al servidor como parámetros en la URL
    const url = `/api/order-stats?startDate=${startDate}&endDate=${endDate}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            console.log('Datos recibidos:', data);
        })
        .catch(error => {
            console.error('Error:', error);
        });

    $('#dateRangeModal').modal('hide');  // Cerrar el modal después de aplicar el filtro
});
