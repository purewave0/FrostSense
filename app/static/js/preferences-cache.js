class PreferencesCache {
    static #KEYS = {
        displayName: 'display_name',
        username: 'username',
        homepage: 'homepage',
        temperatureUnit: 'temperature_unit',
        lastUpdateTime: 'last_update_time',
    }

    /**
     * Store all preferences locally.
     *
     * @param {string} displayName The name others see.
     * @param {string} username Used for logging in.
     * @param {string} homepage The first page the user will see after login.
     * @param {string} temperatureUnit The unit to use for displaying temperatures.
     */
    static set(displayName, username, homepage, temperatureUnit) {
        localStorage.setItem(PreferencesCache.#KEYS.displayName, displayName);
        localStorage.setItem(PreferencesCache.#KEYS.username, username);
        localStorage.setItem(PreferencesCache.#KEYS.homepage, homepage);
        localStorage.setItem(PreferencesCache.#KEYS.temperatureUnit, temperatureUnit);
    }

    /**
     * Get all stored preferences as an object.
     */
    static get() {
        return {
            'displayName': localStorage.getItem(PreferencesCache.#KEYS.displayName),
            'username': localStorage.getItem(PreferencesCache.#KEYS.username),
            'homepage': localStorage.getItem(PreferencesCache.#KEYS.homepage),
            'temperatureUnit': localStorage.getItem(
                PreferencesCache.#KEYS.temperatureUnit
            ),
        };
    }

    /**
     * Get the user's preferred temperature unit. This is a convenience function.
     */
    static getTemperatureUnit() {
        return localStorage.getItem(PreferencesCache.#KEYS.temperatureUnit);
    }

    /** Get the last time the preferences were updated, in UTC milliseconds. */
    static getLastUpdateTime() {
        return localStorage.getItem(PreferencesCache.#KEYS.lastUpdateTime);
    }

    /** Set the last time the preferences were updated, in UTC milliseconds. */
    static setLastUpdateTime(time) {
        return localStorage.setItem(PreferencesCache.#KEYS.lastUpdateTime, time);
    }
};


const PreferencesCacheUpdater = {
    async updateIfNeeded() {
        const response = await Api.fetchPreferencesLastUpdateTime();
        const lastUpdateTime = await response.json();
        if (PreferencesCache.getLastUpdateTime() !== lastUpdateTime) {
            console.log(
                '[preferences.js] stored preferences nonexistent or outdated.'
            );
            PreferencesCache.setLastUpdateTime(lastUpdateTime);
            const preferencesResponse = await Api.fetchPreferences();
            const preferences = await preferencesResponse.json();
            PreferencesCache.set(
                preferences.display_name,
                preferences.username,
                preferences.homepage,
                preferences.temperature_unit
            );
            console.log('[preferences.js] preferences updated.');
        }
    }
}

PreferencesCacheUpdater.updateIfNeeded();
