document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('password-form');
    const formFields = {
        'password': document.getElementById('password'),
        'passwordConfirm': document.getElementById('password-confirm'),
    };

    for (const input of Object.values(formFields)) {
        input.addEventListener('input', () => {
            const notProperlyFilledYet = (
                !formFields.password.validity.valid
                || !formFields.passwordConfirm.validity.valid
            );
            if (notProperlyFilledYet) {
                formFields.passwordConfirm.setCustomValidity('');
                return;
            }

            const passwordValue = formFields.password.value;
            const passwordConfirmationValue = formFields.passwordConfirm.value;

            if (passwordValue !== passwordConfirmationValue) {
                formFields.passwordConfirm
                    .setCustomValidity('The passwords do not match.');
            } else {
                formFields.passwordConfirm.setCustomValidity('');
            }
        });
    }

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        alert('TODO: sucess');
    });
});
