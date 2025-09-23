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
        const passwordValue = formFields.password.value;
        const response = await Api.changeTemporaryPassword(passwordValue);
        if (!response.ok) {
            const error = (await response.json()).error;
            switch (error) {
                case 'same_as_temporary':
                    formFields.password.setCustomValidity(
                        'Your new password cannot be the same as the temporary one.'
                    );
                    formFields.password.reportValidity();
                    formFields.password.focus();
                    formFields.password.setCustomValidity('');
                    break;
                default:
                    showToast(ToastType.ERROR, `Failed to change password (${error})`);
                    break;
            }
            return;
        }

        showToast(ToastType.SUCCESS, 'Password created successfully');
        setTimeout(() => {
            window.location.replace('/');
        }, 1000);
    });
});
