document.addEventListener('DOMContentLoaded', () => {
    const settingsForm = document.getElementById('settings-form');
    const formFields = {
        'defaultTemperatureUnit': document.getElementById('default-temperature-unit'),
        'minimumGaugeValue': document.getElementById('minimum-gauge-value'),
        'maximumGaugeValue': document.getElementById('maximum-gauge-value'),
        'minimumGraphValue': document.getElementById('minimum-graph-value'),
        'maximumGraphValue': document.getElementById('maximum-graph-value'),
    };

    let originalValues = SystemSettingsCache.get();
    formFields.defaultTemperatureUnit.value = originalValues.defaultTemperatureUnit;
    formFields.minimumGaugeValue.value = originalValues.minimumGaugeValue;
    formFields.maximumGaugeValue.value = originalValues.maximumGaugeValue;
    formFields.minimumGraphValue.value = originalValues.minimumGraphValue;
    formFields.maximumGraphValue.value = originalValues.maximumGraphValue;

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
        const minimumGaugeValue = formFields.minimumGaugeValue.value;
        const maximumGaugeValue = formFields.maximumGaugeValue.value;
        const minimumGraphValue = formFields.minimumGraphValue.value;
        const maximumGraphValue = formFields.maximumGraphValue.value;

        // TODO: loading
        const response = await Api.editSystemSettings(
            defaultTemperatureUnit,
            minimumGaugeValue,
            maximumGaugeValue,
            minimumGraphValue,
            maximumGraphValue,
        );
        if (response.ok) {
            leaveEditMode();
            await SystemSettingsCacheUpdater.updateIfNeeded();
            // also update our copy, used for reverting changes in fields
            originalValues = SystemSettingsCache.get();
            // TODO: notify success
            return;
        }
        // TODO: properly handle errors
        const result = await response.json();
        alert(`error updating system settings: ${result.error}`);
    });

    const cancelEditButton = document.getElementById('cancel');
    cancelEditButton.addEventListener('click', () => {
        leaveEditMode();
        revertFields();
    });
});
