const PreferencesCacheUpdater = {
    async updateIfNeeded() {
        const response = await Api.fetchPreferencesLastUpdateTime();
        const lastUpdateTime = await response.json();
        if (PreferencesCache.getLastUpdateTime() !== lastUpdateTime) {
            console.log(
                '[preferences-updater.js] stored preferences nonexistent or outdated.'
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
            console.log('[preferences-updater.js] preferences updated.');
        }
    }
}

PreferencesCacheUpdater.updateIfNeeded();
