Api.fetchProfileLastUpdateTime()
    .then((response) => response.json())
    .then((lastUpdateTime) => {
        if (Profile.getLastUpdateTime() !== lastUpdateTime) {
            console.log('[profile-updater.js] stored profile nonexistent or outdated.');
            Profile.setLastUpdateTime(lastUpdateTime);
            Api.fetchProfile()
                .then((response) => response.json())
                .then((profile) => {
                    console.log('[profile-updater.js] profile updated.');
                    Profile.set(profile.homepage, profile.temperature_unit);
                });
        }
    });
