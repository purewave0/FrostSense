/**
 * LocalStorage cache for the system settings: default temperature unit, value limits
 * for gauges and graphs, and the last time the settings were updated.
 */
class SystemSettingsCache {
    static #PREFIX = 'system_settings';
    static #KEYS = {
        // We only really store the default temperature unit to populate its field
        // in /system-settings.
        defaultTemperatureUnit:
            `${SystemSettingsCache.#PREFIX}.default_temperature_unit`,
        minimumTemperatureValue:
            `${SystemSettingsCache.#PREFIX}.minimum_temperature_value`,
        maximumTemperatureValue:
            `${SystemSettingsCache.#PREFIX}.maximum_temperature_value`,
        updateTimestamp: `${SystemSettingsCache.#PREFIX}.update_timestamp`,
    }

    /**
     * Store all system settings locally.
     *
     * @param {string} defaultTemperatureUnit The default unit for new accounts.
     * @param {number} minimumTemperatureValue Minimum value for gauges and graphs.
     * @param {number} maximumTemperatureValue Maximum value for gauges and graphs.
     */
    static set(
        defaultTemperatureUnit,
        minimumTemperatureValue,
        maximumTemperatureValue,
    ) {
        localStorage.setItem(
            SystemSettingsCache.#KEYS.defaultTemperatureUnit, defaultTemperatureUnit
        );
        localStorage.setItem(
            SystemSettingsCache.#KEYS.minimumTemperatureValue, minimumTemperatureValue
        );
        localStorage.setItem(
            SystemSettingsCache.#KEYS.maximumTemperatureValue, maximumTemperatureValue
        );
    }

    /**
     * Get all stored system settings as an object.
     */
    static get() {
        return {
            'defaultTemperatureUnit': localStorage.getItem(
                SystemSettingsCache.#KEYS.defaultTemperatureUnit
            ),
            'minimumTemperatureValue': localStorage.getItem(
                SystemSettingsCache.#KEYS.minimumTemperatureValue
            ),
            'maximumTemperatureValue': localStorage.getItem(
                SystemSettingsCache.#KEYS.maximumTemperatureValue
            ),
        };
    }

    /**
     * Get the min and max values temperature values. This is a convenience function.
     */
    static getTemperatureLimits() {
        return {
            'minimum': Number(
                localStorage.getItem(
                    SystemSettingsCache.#KEYS.minimumTemperatureValue
                )
            ),
            'maximum': Number(
                localStorage.getItem(
                    SystemSettingsCache.#KEYS.maximumTemperatureValue
                )
            ),
        };
    }

    /** Get the last time the system settings were updated. */
    static getUpdateTimestamp() {
        return localStorage.getItem(SystemSettingsCache.#KEYS.updateTimestamp);
    }

    /** Store the last time the system settings were updated. */
    static setUpdateTimestamp(time) {
        return localStorage.setItem(SystemSettingsCache.#KEYS.updateTimestamp, time);
    }
};


/**
 * Updater for the local system settings cache.
 */
const SystemSettingsCacheUpdater = {
    async updateIfNeeded() {
        const response = await Api.fetchSystemSettingsUpdateTimestamp();
        const updateTimestamp = await response.json();
        if (SystemSettingsCache.getUpdateTimestamp() !== updateTimestamp) {
            console.log(
                '[system-settings-cache.js] stored system settings nonexistent or'
                + ' outdated.'
            );
            SystemSettingsCache.setUpdateTimestamp(updateTimestamp);
            const SystemSettingsResponse = await Api.fetchSystemSettings();
            const SystemSettings = await SystemSettingsResponse.json();
            SystemSettingsCache.set(
                SystemSettings.default_temperature_unit,
                SystemSettings.minimum_temperature_value,
                SystemSettings.maximum_temperature_value,
            );
            console.log('[system-settings-cache.js] system settings updated.');
        }
    }
}

SystemSettingsCacheUpdater.updateIfNeeded();
