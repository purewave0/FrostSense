document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const passwordVisibilityToggle = document.getElementById('password-visibility');
    const rememberLoginCheckbox = document.getElementById('remember-login');

    passwordVisibilityToggle.addEventListener('click', () => {
        if (passwordVisibilityToggle.classList.contains('visible')) {
            passwordInput.type = 'password';
        } else {
            passwordInput.type = 'text';
        }
        passwordVisibilityToggle.classList.toggle('visible');
    });

    function showLoginError() {
        document.body.classList.add('incorrect-login');
    }

    function hideLoginError() {
        document.body.classList.remove('incorrect-login');
    }

    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        hideLoginError();

        const username = usernameInput.value.trim();
        const password = passwordInput.value.trim();
        const response = await Api.login(
            username, password, rememberLoginCheckbox.checked
        );
        if (!response.ok) {
            const error = (await response.json()).error;
            switch (error) {
                case 'incorrect_login':
                    showLoginError();
                    break;
                default:
                    showToast(ToastType.ERROR, `Failed to log in (${error})`);
                    break;
            }
            return;
        }

        document.location.href = '/';
    });
});
