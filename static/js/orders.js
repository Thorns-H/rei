
let currentPage = 1;
const itemsPerPage = 2;
const orders = document.querySelectorAll('.order-card');

function showPage(page) {
    const start = (page - 1) * itemsPerPage;
    const end = start + itemsPerPage;

    orders.forEach((order, index) => {
        order.style.display = (index >= start && index < end) ? 'block' : 'none';
    });

    document.getElementById('prevPageBtn').disabled = (page === 1);
    document.getElementById('nextPageBtn').disabled = (end >= orders.length);
}


function changePage(step) {
    currentPage += step;
    showPage(currentPage);
}

showPage(currentPage);