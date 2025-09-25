const Api = {
    fetchSensors() {
        return fetch('/api/sensors');
    },

    fetchLastSensorReadings() {
        return fetch('/api/sensors/last-readings');
    },

    fetchSensorReadingsByDays(sensorIds, startDates, offsetIds = null) {
        let queryString = '';
        const encodedISODates = startDates.map(
            (date) => encodeURIComponent(date.toISOString())
        );
        queryString += `?start_dates=${encodedISODates.join(',')}`;
        queryString += `&sensor_ids=${sensorIds.join(',')}`;
        if (offsetIds) {
            queryString += `&offset_ids=${offsetIds.join(',')}`;
        }

        return fetch('/api/sensors/readings' + queryString);
    },

    fetchTodayReadingsCounts() {
        return fetch('/api/sensors/readings-count/today');
    },

    fetchSensorReadingsInTimeRange(sensorId, rangeStart, rangeEnd) {
        return fetch(
            `/api/sensors/${sensorId}/readings-count`
            + `?range_start=${encodeURIComponent(rangeStart)}`
            + `&range_end=${encodeURIComponent(rangeEnd)}`
        );
    },

    editSensor(sensorId, name) {
        return fetch(`/api/sensors/${sensorId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: name,
            })
        });
    },

    createReport(sensorId, rangeStart, rangeEnd, dataFormat, notes) {
        return fetch('/api/reports', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                'sensor_id': sensorId,
                'range_start': rangeStart.toISOString(),
                'range_end': rangeEnd.toISOString(),
                'data_format': dataFormat,
                'notes': (notes) ? notes.trim() : null,
            })
        });
    },

    login(username, password, shouldRememberLogin) {
        return fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                'username': username,
                'password': password,
                'remember_login': shouldRememberLogin,
            })
        });
    },

    createPassword(newPassword) {
        return fetch('/api/me/permanent-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                'password': newPassword,
            })
        });
    },

    changePassword(currentPassword, newPassword) {
        return fetch('/api/me/password', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                'current_password': currentPassword,
                'password': newPassword,
            })
        });
    },

    getLastPasswordChangeDate() {
        return fetch('/api/me/last-password-change-time');
    },

    fetchUsers(updatedAfter = null) {
        let url = '/api/users'
        if (updatedAfter) {
            url += `?updated-after=${updatedAfter.toISOString()}`
        }
        return fetch(url);
    },

    fetchUsersSummary(updatedAfter) {
        let url = `/api/users/summary?updated-after=${updatedAfter.toISOString()}`;
        return fetch(url);
    },

    createUser(displayName, username, permissionsValue) {
        return fetch('/api/users', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                'display_name': displayName,
                'username': username,
                'permissions': permissionsValue,
            })
        });
    },

    editUser(userId, displayName, permissionsValue) {
        return fetch(`/api/users/${userId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                'display_name': displayName,
                'permissions': permissionsValue,
            })
        });
    },

    resetUserPassword(userId) {
        return fetch(`/api/users/${userId}/reset-password`, { method: 'POST', });
    },

    deleteUser(userId) {
        return fetch(`/api/users/${userId}`, { method: 'DELETE', });
    },

    editPreferences(displayName, username, homepage, temperatureUnit) {
        return fetch('/api/me/preferences', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                'display_name': displayName,
                'username': username,
                'homepage': homepage,
                'temperature_unit': temperatureUnit,
            })
        });
    },

    fetchPreferences() {
        return fetch('/api/me/preferences');
    },

    fetchPreferencesLastUpdateTime() {
        return fetch('/api/me/preferences/last-update-time');
    },

    fetchSystemSettings() {
        return fetch('/api/system-settings');
    },

    fetchSystemSettingsUpdateTimestamp() {
        return fetch('/api/system-settings/last-update-time');
    },

    editSystemSettings(
        defaultTemperatureUnit,
        minimumGaugeValue,
        maximumGaugeValue,
        minimumGraphValue,
        maximumGraphValue,
    ) {
        return fetch('/api/system-settings', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                'default_temperature_unit': defaultTemperatureUnit,
                'minimum_gauge_value': minimumGaugeValue,
                'maximum_gauge_value': maximumGaugeValue,
                'minimum_graph_value': minimumGraphValue,
                'maximum_graph_value': maximumGraphValue,
            })
        });
    }
};
