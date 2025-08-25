const ProfileUpdater = {
    async updateIfNeeded() {
        const response = await Api.fetchProfileLastUpdateTime();
        const lastUpdateTime = await response.json();
        if (Profile.getLastUpdateTime() !== lastUpdateTime) {
            console.log('[profile-updater.js] stored profile nonexistent or outdated.');
            Profile.setLastUpdateTime(lastUpdateTime);
            const profileResponse = await Api.fetchProfile();
            const profile = await profileResponse.json();
            Profile.set(
                profile.display_name,
                profile.username,
                profile.homepage,
                profile.temperature_unit
            );
            console.log('[profile-updater.js] profile updated.');
        }
    }
}

ProfileUpdater.updateIfNeeded();
