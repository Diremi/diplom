document.addEventListener('DOMContentLoaded', function() {
    // Переключение видимости пароля
    const passwordToggle = document.getElementById('passwordToggle');
    const passwordField = document.getElementById('id_password1');
    
    const confirmPasswordToggle = document.getElementById('confirmPasswordToggle');
    const confirmPasswordField = document.getElementById('id_password2');
    
    function togglePasswordVisibility(field, toggle) {
        if (!field || !toggle) return;
        
        const type = field.getAttribute('type') === 'password' ? 'text' : 'password';
        field.setAttribute('type', type);
        
        const icon = toggle.querySelector('i');
        if (icon) {
            icon.classList.toggle('bi-eye');
            icon.classList.toggle('bi-eye-slash');
        }
    }
    
    if (passwordToggle && passwordField) {
        passwordToggle.addEventListener('click', () => {
            togglePasswordVisibility(passwordField, passwordToggle);
        });
    }
    
    if (confirmPasswordToggle && confirmPasswordField) {
        confirmPasswordToggle.addEventListener('click', () => {
            togglePasswordVisibility(confirmPasswordField, confirmPasswordToggle);
        });
    }
    
    // Маска для телефона
    const phoneField = document.getElementById('id_phone');
    if (phoneField) {
        phoneField.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            
            // Обработка российских номеров
            if (value.startsWith('7') || value.startsWith('8')) {
                value = '7' + value.substring(1);
            } else if (value.length > 0) {
                value = '7' + value;
            }
            
            // Форматирование
            let formattedValue = '+7';
            if (value.length > 1) {
                formattedValue += ' (' + value.substring(1, 4);
            }
            if (value.length > 4) {
                formattedValue += ') ' + value.substring(4, 7);
            }
            if (value.length > 7) {
                formattedValue += '-' + value.substring(7, 9);
            }
            if (value.length > 9) {
                formattedValue += '-' + value.substring(9, 11);
            }
            
            e.target.value = formattedValue;
        });
    }
    
    // Автофокус на первое поле с ошибкой
    const firstErrorField = document.querySelector('.is-invalid');
    if (firstErrorField) {
        firstErrorField.focus();
    }
});