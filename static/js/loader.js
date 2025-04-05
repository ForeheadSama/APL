// Function to check the loading status
function checkStatus() {
    fetch('/status')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Update progress bar if exists
            const progressBar = document.getElementById('progress-bar');
            if (progressBar && data.data) {
                progressBar.style.width = `${data.data.progress}%`;
                progressBar.textContent = `${data.data.progress}%`;
            }

            // Update status message if exists
            const statusMessage = document.getElementById('status-message');
            if (statusMessage && data.data) {
                statusMessage.textContent = data.data.message;
            }

            // Handle redirect
            if (data.redirect) {
                // Small delay for visual feedback
                setTimeout(() => {
                    window.location.href = data.redirect;
                }, 500);
            } else if (data.data && !data.data.error) {
                // Continue polling if not complete
                setTimeout(checkStatus, 500);
            } else if (data.data && data.data.error) {
                // Show error message
                document.getElementById('error-message').textContent = data.data.error;
                document.getElementById('retry-button').style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Error checking status:', error);
            document.getElementById('error-message').textContent = 
                'Connection error. Retrying...';
            setTimeout(checkStatus, 1000);
        });
}

// Start checking status when page loads
document.addEventListener('DOMContentLoaded', () => {
    checkStatus();
    
    // Retry button handler if you want one
    document.getElementById('retry-button')?.addEventListener('click', () => {
        document.getElementById('error-message').textContent = 'Retrying...';
        document.getElementById('retry-button').style.display = 'none';
        checkStatus();
    });
});