document.addEventListener('DOMContentLoaded', () => {
    const buttonChangePassword = document.getElementById('button-change-password');
    const passwordChangeTimeValue = document.getElementById('password-changed-on');

    async function updatePasswordChangeDate() {
        return Api.getLastPasswordChangeDate()
            .then((response) => response.json())
            .then((passwordChangedDate) => {
                if (passwordChangedDate === null) {
                    passwordChangeTimeValue.textContent = 'never';
                    return;
                }
                passwordChangeTimeValue.textContent =
                    formatDateToCompactDatetime(new Date(passwordChangedDate));
            });
    }

    updatePasswordChangeDate();

    buttonChangePassword.addEventListener('click', () => {
        openChangePasswordModal();
    });

    const changePasswordModal = {
        'form': document.getElementById('modal-change-password-form'),
        'currentPassword':
            document.getElementById('modal-change-password-current-password'),
        'password': document.getElementById('modal-change-password-password'),
        'passwordConfirm':
            document.getElementById('modal-change-password-password-confirm'),
    };
    for (const input of [
        changePasswordModal.password, changePasswordModal.passwordConfirm
    ]) {
        input.addEventListener('input', () => {
            const notProperlyFilledYet = (
                !changePasswordModal.password.validity.valid
                || !changePasswordModal.passwordConfirm.validity.valid
            );
            if (notProperlyFilledYet) {
                changePasswordModal.passwordConfirm.setCustomValidity('');
                return;
            }

            const passwordValue = changePasswordModal.password.value;
            const passwordConfirmationValue = changePasswordModal.passwordConfirm.value;

            if (passwordValue !== passwordConfirmationValue) {
                changePasswordModal.passwordConfirm
                    .setCustomValidity('The passwords do not match.');
            } else {
                changePasswordModal.passwordConfirm.setCustomValidity('');
            }
        });
    }
    changePasswordModal.form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const currentPassword = changePasswordModal.currentPassword.value;
        const newPassword = changePasswordModal.password.value;

        const response = await Api.changePassword(
            currentPassword, newPassword
        );

        if (!response.ok) {
            const error = (await response.json()).error;
            switch (error) {
                case 'incorrect_current_password':
                    changePasswordModal.currentPassword
                        .setCustomValidity('Incorrect password.');
                    changePasswordModal.currentPassword.reportValidity();
                    changePasswordModal.currentPassword.focus();
                    changePasswordModal.currentPassword.setCustomValidity('');
                    break;
                default:
                    MicroModal.close('modal-change-password');
                    showToast(
                        ToastType.ERROR, `Failed to change password (${error})`
                    );
                    break;
            }
            return;
        }

        MicroModal.close('modal-change-password');
        changePasswordModal.form.reset();
        showToast(ToastType.SUCCESS, 'Password changed successfully');
        updatePasswordChangeDate();
    });

    function openChangePasswordModal() {
        changePasswordModal.form.reset();
        MicroModal.show('modal-change-password');
    }
});
