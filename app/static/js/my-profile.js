document.addEventListener('DOMContentLoaded', () => {
    const profileForm = document.getElementById('profile-form');

    const editButton = document.getElementById('edit-button');
    const displayedNames = {
        'displayName': document.getElementById('displayed-display-name'),
        'username': document.getElementById('displayed-username'),
    };
    const formFields = {
        'displayName': document.getElementById('display-name'),
        'username': document.getElementById('username'),
        'homepage': document.getElementById('homepage'),
        'temperatureUnit': document.getElementById('temperature-unit'),
    };

    let originalProfile = Profile.get();
    formFields.homepage.value = originalProfile.homepage;
    formFields.temperatureUnit.value = originalProfile.temperatureUnit;
    editButton.disabled = false;

    function enterEditMode() {
        editButton.disabled = true;
        profileForm.classList.add('editing');
        for (const id in formFields) {
            formFields[id].disabled = false;
        }
    }

    function leaveEditMode() {
        editButton.disabled = false;
        profileForm.classList.remove('editing');
        for (const id in formFields) {
            formFields[id].disabled = true;
        }
    }

    function revertFields() {
        for (const fieldKey in formFields) {
            formFields[fieldKey].value = originalProfile[fieldKey];
        }
    }

    editButton.addEventListener('click', enterEditMode);

    const cancelEditButton = document.getElementById('cancel');
    cancelEditButton.addEventListener('click', () => {
        leaveEditMode();
        revertFields();
    });

    profileForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const displayName = formFields.displayName.value.trim();
        const username = formFields.username.value.trim();
        // TODO: check if username is unique

        const homepage = formFields.homepage.value;
        const temperatureUnit = formFields.temperatureUnit.value;

        // TODO: loading
        const response = await Api.editProfile(
            displayName,
            username,
            homepage,
            temperatureUnit
        );
        if (response.ok) {
            leaveEditMode();
            displayedNames.displayName.textContent = displayName;
            displayedNames.username.textContent = username;
            await ProfileUpdater.updateIfNeeded();
            // also update our copy, used for reverting changes in fields
            originalProfile = Profile.get();
            // TODO: notify success
            return;
        }
        // TODO: properly handle errors
        const result = await response.json();
        alert(`error updating profile: ${result.error}`);
    });
});
