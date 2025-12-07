fetch('/profile/status')
    .then(response => response.json())
    .then(data => {
        const statusElement = document.getElementById('user-status');
        if (data.is_active) {
            statusElement.textContent = 'Активен';
            statusElement.classList.remove('status-disabled');
            statusElement.classList.add('status-enabled');
        } else {
            statusElement.textContent = 'Неактивен';
            statusElement.classList.remove('status-enabled');
            statusElement.classList.add('status-disabled');
        }
    })
    .catch(error => {
        console.error('Error fetching user status:', error);
        document.getElementById('user-status').textContent = 'Ошибка загрузки';
    });