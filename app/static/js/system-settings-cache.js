class SystemSettingsCache {
    static #PREFIX = 'system_settings';
    static #KEYS = {
        // We only really store the default temperature unit to populate its field
        // in /system-settings.
        defaultTemperatureUnit:
            `${SystemSettingsCache.#PREFIX}.default_temperature_unit`,
        minimumGaugeValue: `${SystemSettingsCache.#PREFIX}.minimum_gauge_value`,
        maximumGaugeValue: `${SystemSettingsCache.#PREFIX}.maximum_gauge_value`,
        minimumGraphValue: `${SystemSettingsCache.#PREFIX}.minimum_graph_value`,
        maximumGraphValue: `${SystemSettingsCache.#PREFIX}.maximum_graph_value`,
        updateTimestamp: `${SystemSettingsCache.#PREFIX}.update_timestamp`,
    }

    /**
     * Store all system settings locally.
     *
     * @param {string} defaultTemperatureUnit The default unit for new accounts.
     * @param {number} minimumGaugeValue Minimum value for all gauges.
     * @param {number} maximumGaugeValue Maximum value for all gauges.
     * @param {number} minimumGraphValue Minimum value for all graphs.
     * @param {number} maximumGraphValue Maximum value for all graphs.
     */
    static set(
        defaultTemperatureUnit,
        minimumGaugeValue,
        maximumGaugeValue,
        minimumGraphValue,
        maximumGraphValue
    ) {
        localStorage.setItem(
            SystemSettingsCache.#KEYS.defaultTemperatureUnit, defaultTemperatureUnit
        );
        localStorage.setItem(
            SystemSettingsCache.#KEYS.minimumGaugeValue, minimumGaugeValue
        );
        localStorage.setItem(
            SystemSettingsCache.#KEYS.maximumGaugeValue, maximumGaugeValue
        );
        localStorage.setItem(
            SystemSettingsCache.#KEYS.minimumGraphValue, minimumGraphValue
        );
        localStorage.setItem(
            SystemSettingsCache.#KEYS.maximumGraphValue, maximumGraphValue
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
            'minimumGaugeValue': localStorage.getItem(
                SystemSettingsCache.#KEYS.minimumGaugeValue
            ),
            'maximumGaugeValue': localStorage.getItem(
                SystemSettingsCache.#KEYS.maximumGaugeValue
            ),
            'minimumGraphValue': localStorage.getItem(
                SystemSettingsCache.#KEYS.minimumGraphValue
            ),
            'maximumGraphValue': localStorage.getItem(
                SystemSettingsCache.#KEYS.maximumGraphValue
            ),
        };
    }

    /**
     * Get the min and max values for gauges. This is a convenience function.
     */
    static getGaugeLimits() {
        return {
            'minimum': localStorage.getItem(
                SystemSettingsCache.#KEYS.minimumGaugeValue
            ),
            'maximum': localStorage.getItem(
                SystemSettingsCache.#KEYS.minimumGaugeValue
            ),
        };
    }

    /**
     * Get the min and max values for graphs. This is a convenience function.
     */
    static getGraphLimits() {
        return {
            'minimum': localStorage.getItem(
                SystemSettingsCache.#KEYS.minimumGraphValue
            ),
            'maximum': localStorage.getItem(
                SystemSettingsCache.#KEYS.minimumGraphValue
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
                SystemSettings.minimum_gauge_value,
                SystemSettings.maximum_gauge_value,
                SystemSettings.minimum_graph_value,
                SystemSettings.maximum_graph_value,
            );
            console.log('[system-settings-cache.js] system settings updated.');
        }
    }
}

SystemSettingsCacheUpdater.updateIfNeeded();
