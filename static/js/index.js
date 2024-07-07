
document.addEventListener('DOMContentLoaded', function () {
    fetch('/api/order-stats')
        .then(response => response.json())
        .then(data => {
            var ctx = document.getElementById('orderChart').getContext('2d');
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Ganancia', 'Inversión', 'Pendiente'],
                    datasets: [{
                        data: [data.profit, data.invest, data.pending],
                        backgroundColor: ['#28a745', '#ffc107', '#dc3545']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        tooltip: {
                            callbacks: {
                                label: function(tooltipItem) {
                                    return tooltipItem.label + ': $' + tooltipItem.raw.toFixed(2);
                                }
                            }
                        }
                    }
                }
            });
        });
});
