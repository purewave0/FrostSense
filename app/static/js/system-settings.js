document.addEventListener('DOMContentLoaded', () => {
    const settingsForm = document.getElementById('settings-form');
    const formFields = {
        'defaultTemperatureUnit': document.getElementById('default-temperature-unit'),
        'minimumTemperatureValue': document.getElementById('minimum-temperature-value'),
        'maximumTemperatureValue': document.getElementById('maximum-temperature-value'),
    };

    let originalValues = SystemSettingsCache.get();
    formFields.defaultTemperatureUnit.value = originalValues.defaultTemperatureUnit;
    formFields.minimumTemperatureValue.value = originalValues.minimumTemperatureValue;
    formFields.maximumTemperatureValue.value = originalValues.maximumTemperatureValue;

    let changedFields = {};

    /**
     * Return whether any field had its value changed by the user.
     */
    function wasAnyFieldChanged() {
        for (const fieldName in changedFields) {
            return true;
        }
        return false;
    }

    /**
     * Show the Edit controls (Cancel and Apply buttons).
     */
    function enterEditMode() {
        settingsForm.classList.add('editing');
    }

    /**
     * Hide the Edit controls (Cancel and Apply buttons).
     */
    function leaveEditMode() {
        settingsForm.classList.remove('editing');
        changedFields = {};
    }

    /**
     * Revert all fields to their original values.
     */
    function revertFields() {
        for (const fieldName in formFields) {
            formFields[fieldName].value = originalValues[fieldName];
        }
    }

    const originalSettings = SystemSettingsCache.get();
    for (const fieldName in formFields) {
        const field = formFields[fieldName];

        field.addEventListener('change', () => {
            if (field.value !== originalValues[fieldName]) {
                changedFields[fieldName] = field;
            } else {
                delete changedFields[fieldName];
            }

            if (wasAnyFieldChanged()) {
                enterEditMode();
            } else {
                leaveEditMode();
            }
        });
    }

    settingsForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const defaultTemperatureUnit = formFields.defaultTemperatureUnit.value;
        const minimumTemperatureValue = formFields.minimumTemperatureValue.value;
        const maximumTemperatureValue = formFields.maximumTemperatureValue.value;

        // TODO: loading
        const response = await Api.editSystemSettings(
            defaultTemperatureUnit,
            minimumTemperatureValue,
            maximumTemperatureValue,
        );
        if (!response.ok) {
            const error = (await response.json()).error;
            showToast(
                ToastType.ERROR, `Failed to apply changes (${error})`
            );
            return;
        }

        leaveEditMode();
        showToast(
            ToastType.SUCCESS, 'Applied changes successfully'
        );
        await SystemSettingsCacheUpdater.updateIfNeeded();
        // also update our copy, used for reverting changes in fields
        originalValues = SystemSettingsCache.get();
    });

    const cancelEditButton = document.getElementById('cancel');
    cancelEditButton.addEventListener('click', () => {
        leaveEditMode();
        revertFields();
    });
});
