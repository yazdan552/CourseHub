document.addEventListener('DOMContentLoaded', function() {

    // ================ نمودار ثبت‌نام‌ها ================
    const enrollmentCtx = document.getElementById('enrollmentChart');
    if (enrollmentCtx) {
        new Chart(enrollmentCtx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: typeof enrollmentLabels !== 'undefined' ? enrollmentLabels : [],
                datasets: [{
                    label: 'Enrollments',
                    data: typeof enrollmentData !== 'undefined' ? enrollmentData : [],
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }

    // ================ نمودار درآمد ================
    const revenueCtx = document.getElementById('revenueChart');
    if (revenueCtx) {
        new Chart(revenueCtx.getContext('2d'), {
            type: 'line',
            data: {
                labels: typeof revenueLabels !== 'undefined' ? revenueLabels : [],
                datasets: [{
                    label: 'Revenue ($)',
                    data: typeof revenueData !== 'undefined' ? revenueData : [],
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value;
                            }
                        }
                    }
                }
            }
        });
    }

});