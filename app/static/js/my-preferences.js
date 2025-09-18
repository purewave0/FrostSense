document.addEventListener('DOMContentLoaded', () => {
    const preferencesForm = document.getElementById('preferences-form');

    const editButton = document.getElementById('edit-button');
    const displayedUsername = document.getElementById('displayed-username');
    const formFields = {
        'username': document.getElementById('username'),
        'homepage': document.getElementById('homepage'),
        'temperatureUnit': document.getElementById('temperature-unit'),
    };

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
        const username = formFields.username.value.trim();
        // TODO: check if username is unique

        const homepage = formFields.homepage.value;
        const temperatureUnit = formFields.temperatureUnit.value;

        // TODO: loading
        const response = await Api.editPreferences(
            username,
            homepage,
            temperatureUnit
        );
        if (response.ok) {
            leaveEditMode();
            displayedUsername.textContent = username;
            await PreferencesCacheUpdater.updateIfNeeded();
            // also update our copy, used for reverting changes in fields
            originalPreferences = PreferencesCache.get();
            // TODO: notify success
            return;
        }
        // TODO: properly handle errors
        const result = await response.json();
        alert(`error updating preferences: ${result.error}`);
    });
});
