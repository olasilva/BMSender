document.addEventListener('DOMContentLoaded', function() {
    // Add basic form validation
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const subject = document.getElementById('subject').value.trim();
            const body = document.getElementById('body').value.trim();
            const recipients = document.getElementById('recipients').value.trim();
            
            if (!subject) {
                e.preventDefault();
                alert('Please enter an email subject');
                return false;
            }
            
            if (!body) {
                e.preventDefault();
                alert('Please enter an email body');
                return false;
            }
            
            if (!recipients) {
                e.preventDefault();
                alert('Please enter at least one recipient email');
                return false;
            }
        });
    }
    
    // Auto-close alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});