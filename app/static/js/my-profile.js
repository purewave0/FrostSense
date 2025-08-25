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

    const profile = Profile.get();
    formFields.homepage.value = profile.homepage;
    formFields.temperatureUnit.value = profile.temperatureUnit;
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

    editButton.addEventListener('click', enterEditMode);

    const cancelEditButton = document.getElementById('cancel');
    // TODO: when cancelling, revert all values
    cancelEditButton.addEventListener('click', leaveEditMode);

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
            ProfileUpdater.updateIfNeeded();
            // TODO: notify success
            return;
        }
        // TODO: properly handle errors
        const result = await response.json();
        alert(`error updating profile: ${result.error}`);
    });
});
