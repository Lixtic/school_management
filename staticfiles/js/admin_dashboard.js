// Admin Dashboard Charts
document.addEventListener('DOMContentLoaded', function() {
    // Students by Class Chart
    const classNamesData = window.chartData?.classNames || [];
    const studentCountsData = window.chartData?.studentCounts || [];
    
    if (classNamesData && classNamesData.length > 0 && studentCountsData) {
        const studentsCtx = document.getElementById('studentsByClassChart');
        if (studentsCtx) {
            new Chart(studentsCtx.getContext('2d'), {
                type: 'doughnut',
                data: {
                    labels: classNamesData,
                    datasets: [{
                        data: studentCountsData,
                        backgroundColor: [
                            '#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6',
                            '#1abc9c', '#34495e', '#e67e22'
                        ],
                        borderColor: '#fff',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 15,
                                font: { size: 12 }
                            }
                        }
                    }
                }
            });
        }
    }

    // Attendance Chart
    const attendanceLabelsData = window.chartData?.attendanceLabels || [];
    const presentCountData = window.chartData?.presentCount || [];
    const absentCountData = window.chartData?.absentCount || [];
    
    if (attendanceLabelsData && attendanceLabelsData.length > 0 && presentCountData && absentCountData) {
        const attendanceCtx = document.getElementById('attendanceChart');
        if (attendanceCtx) {
            new Chart(attendanceCtx.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: attendanceLabelsData,
                    datasets: [
                        {
                            label: 'Present',
                            data: presentCountData,
                            backgroundColor: '#2ecc71',
                            borderRadius: 4,
                            borderSkipped: false
                        },
                        {
                            label: 'Absent',
                            data: absentCountData,
                            backgroundColor: '#e74c3c',
                            borderRadius: 4,
                            borderSkipped: false
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    indexAxis: 'x',
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 10
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: {
                                padding: 15,
                                font: { size: 12 }
                            }
                        }
                    }
                }
            });
        }
    }
});
