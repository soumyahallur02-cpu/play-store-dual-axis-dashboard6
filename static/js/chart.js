let chartInstance = null;
let demoOverride = false;

function checkTimeAndRender() {
    const now = new Date();
    const utc = now.getTime() + (now.getTimezoneOffset() * 60000);
    const istTime = new Date(utc + (3600000 * 5.5));
    
    const istHours = istTime.getHours();
    const istMinutes = istTime.getMinutes();
    const istSeconds = istTime.getSeconds();

    const formattedTime = `${String(istHours).padStart(2, '0')}:${String(istMinutes).padStart(2, '0')}:${String(istSeconds).padStart(2, '0')} IST`;
    
    document.getElementById('timeBadge').innerText = `IST Time: ${formattedTime}`;
    document.getElementById('clockTime').innerText = formattedTime;

    // Active Window: 13:00 to 14:00 IST (1 PM - 2 PM IST)
    const isInWindow = (istHours >= 13 && istHours < 14);

    const gateMessage = document.getElementById('gateMessage');
    const chartSection = document.getElementById('chartSection');

    if (isInWindow || demoOverride) {
        gateMessage.classList.add('hidden');
        chartSection.classList.remove('hidden');
        if (!chartInstance) {
            fetchAndRenderChart();
        }
    } else {
        gateMessage.classList.remove('hidden');
        chartSection.classList.add('hidden');
    }
}

function toggleOverride() {
    demoOverride = !demoOverride;
    checkTimeAndRender();
}

async function fetchAndRenderChart() {
    try {
        const response = await fetch('/api/dual-axis-data');
        const res = await response.json();
        const data = res.data;

        const ctx = document.getElementById('dualAxisChart').getContext('2d');

        chartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.categories,
                datasets: [
                    {
                        label: 'Free Apps - Avg Installs (Left Axis)',
                        data: data.free_installs,
                        backgroundColor: 'rgba(56, 189, 248, 0.85)',
                        borderColor: '#38bdf8',
                        borderWidth: 1,
                        yAxisID: 'yInstalls'
                    },
                    {
                        label: 'Paid Apps - Avg Installs (Left Axis)',
                        data: data.paid_installs,
                        backgroundColor: 'rgba(99, 102, 241, 0.85)',
                        borderColor: '#6366f1',
                        borderWidth: 1,
                        yAxisID: 'yInstalls'
                    },
                    {
                        label: 'Paid Apps - Avg Revenue ($) (Right Axis)',
                        type: 'line',
                        data: data.paid_revenue,
                        borderColor: '#f59e0b',
                        backgroundColor: '#f59e0b',
                        borderWidth: 3,
                        pointRadius: 6,
                        pointHoverRadius: 8,
                        yAxisID: 'yRevenue'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#94a3b8', font: { family: 'Inter', size: 12, weight: 'bold' } }
                    },
                    yInstalls: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Average Installs',
                            color: '#38bdf8',
                            font: { family: 'Inter', size: 12, weight: 'bold' }
                        },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: {
                            color: '#38bdf8',
                            callback: value => value >= 1e6 ? (value/1e6).toFixed(1) + 'M' : value.toLocaleString()
                        }
                    },
                    yRevenue: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Average Revenue ($)',
                            color: '#f59e0b',
                            font: { family: 'Inter', size: 12, weight: 'bold' }
                        },
                        grid: { drawOnChartArea: false },
                        ticks: {
                            color: '#f59e0b',
                            callback: value => '$' + (value >= 1e3 ? (value/1e3).toFixed(0) + 'K' : value)
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: { color: '#f1f5f9', font: { family: 'Inter', size: 12 } }
                    }
                }
            }
        });
    } catch (err) {
        console.error('Error fetching data:', err);
    }
}

checkTimeAndRender();
setInterval(checkTimeAndRender, 10000);