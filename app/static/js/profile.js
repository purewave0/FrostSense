class Profile {
    static #KEYS = {
        displayName: 'display_name',
        username: 'username',
        homepage: 'homepage',
        temperatureUnit: 'temperature_unit',
        lastUpdateTime: 'last_update_time',
    }

    /**
     * Store all profile preferences locally.
     *
     * @param {string} displayName The name others see.
     * @param {string} username Used for logging in.
     * @param {string} homepage The first page the user will see after login.
     * @param {string} temperatureUnit The unit to use for displaying temperatures.
     */
    static set(displayName, username, homepage, temperatureUnit) {
        localStorage.setItem(Profile.#KEYS.displayName, displayName);
        localStorage.setItem(Profile.#KEYS.username, username);
        localStorage.setItem(Profile.#KEYS.homepage, homepage);
        localStorage.setItem(Profile.#KEYS.temperatureUnit, temperatureUnit);
    }

    /**
     * Get all stored profile preferences as an object.
     */
    static get() {
        return {
            'displayName': localStorage.getItem(Profile.#KEYS.displayName),
            'username': localStorage.getItem(Profile.#KEYS.username),
            'homepage': localStorage.getItem(Profile.#KEYS.homepage),
            'temperatureUnit': localStorage.getItem(Profile.#KEYS.temperatureUnit),
        };
    }

    /**
     * Get the user's preferred temperature unit. This is a convenience function.
     */
    static getTemperatureUnit() {
        return localStorage.getItem(Profile.#KEYS.temperatureUnit);
    }

    /** Get the last time the profile was updated, in UTC milliseconds. */
    static getLastUpdateTime() {
        return localStorage.getItem(Profile.#KEYS.lastUpdateTime);
    }

    /** Set the last time the profile was updated, in UTC milliseconds. */
    static setLastUpdateTime(time) {
        return localStorage.setItem(Profile.#KEYS.lastUpdateTime, time);
    }
};
