/**
 * Cheryl Dashboard
 * Dashboard-specific functionality
 */

document.addEventListener('DOMContentLoaded', () => {
    // Animate stat cards on load
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach((card, index) => {
        setTimeout(() => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'all 0.5s ease';

            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 50);
        }, index * 100);
    });

    // Simulate real-time updates (demo)
    setInterval(() => {
        updateDashboardData();
    }, 30000); // Update every 30 seconds

    // Initialize tooltips/popovers if needed
    initializeInteractivity();
});

function updateDashboardData() {
    // In production, this would fetch real data from the API
    console.log('Dashboard data updated');
}

function initializeInteractivity() {
    // Add click handlers for cards
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach(card => {
        card.style.cursor = 'pointer';
        card.addEventListener('click', function() {
            const label = this.querySelector('.stat-card-label')?.textContent;
            if (label) {
                console.log('Clicked:', label);
                // Navigate to relevant page or show details
            }
        });
    });
}
