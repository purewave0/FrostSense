document.addEventListener('DOMContentLoaded', () => {
    const preferencesForm = document.getElementById('preferences-form');

    const editButton = document.getElementById('edit-button');
    const displayedDisplayName = document.getElementById('displayed-display-name');
    const displayedUsername = document.getElementById('displayed-username');
    const formFields = {
        'username': document.getElementById('username'),
        'homepage': document.getElementById('homepage'),
        'temperatureUnit': document.getElementById('temperature-unit'),
    };
    if (document.body.classList.contains('is-admin')) {
        formFields.displayName = document.getElementById('display-name');
    }

    let originalPreferences = PreferencesCache.get();
    formFields.homepage.value = originalPreferences.homepage;
    formFields.temperatureUnit.value = originalPreferences.temperatureUnit;
    editButton.disabled = false;

    function enterEditMode() {
        editButton.disabled = true;
        preferencesForm.classList.add('editing');
        for (const id in formFields) {
            formFields[id].disabled = false;
        }
    }

    function leaveEditMode() {
        editButton.disabled = false;
        preferencesForm.classList.remove('editing');
        for (const id in formFields) {
            formFields[id].disabled = true;
        }
    }

    function revertFields() {
        for (const fieldKey in formFields) {
            formFields[fieldKey].value = originalPreferences[fieldKey];
        }
    }

    editButton.addEventListener('click', enterEditMode);

    const cancelEditButton = document.getElementById('cancel');
    cancelEditButton.addEventListener('click', () => {
        leaveEditMode();
        revertFields();
    });

    preferencesForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const displayName = document.getElementById('display-name').value.trim();
        const username = formFields.username.value.trim();

        const homepage = formFields.homepage.value;
        const temperatureUnit = formFields.temperatureUnit.value;

        if (
            displayName === originalPreferences.displayName
            && username === originalPreferences.username
            && homepage === originalPreferences.homepage
            && temperatureUnit === originalPreferences.temperatureUnit
        ) {
            leaveEditMode();
            revertFields();  // remove any trailing whitespace, etc.
            showToast(ToastType.NO_CHANGES, `No changes made`);
            return;
        }

        // TODO: loading
        // TODO: disable Apply button while it's loading
        const response = await Api.editPreferences(
            displayName,
            username,
            homepage,
            temperatureUnit
        );
        if (!response.ok) {
            const error = (await response.json()).error;
            switch (error) {
                case 'username_already_exists':
                    formFields.username
                        .setCustomValidity('This username already exists.');
                    formFields.username.reportValidity();
                    formFields.username.focus();
                    formFields.username.setCustomValidity('');
                    break;
                default:
                    showToast(
                        ToastType.ERROR, `Failed to apply preferences (${error})`
                    );
                    break;
            }
            return;
        }

        leaveEditMode();
        displayedDisplayName.textContent = displayName;
        displayedUsername.textContent = username;
        await PreferencesCacheUpdater.updateIfNeeded();
        // also update our copy, used for reverting changes in fields
        originalPreferences = PreferencesCache.get();

        showToast(
            ToastType.SUCCESS, `Applied preferences successfully`
        );
    });
});
