document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');

    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const username = usernameInput.value.trim();
        const password = passwordInput.value.trim();
        const response = await Api.login(username, password);
        console.log(response);
        if (response.ok) {
            document.location.href = '/readings';
        } else {
            // TODO: proper error
            alert('incorrect username or password.');
        }
    });

});
