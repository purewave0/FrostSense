const Api = {
    fetchSensors() {
        return fetch('/api/sensors');
    },

    fetchLatestSensorReadings() {
        return fetch('/api/sensors/latest-readings');
    },

    fetchTodayReadingsCounts() {
        return fetch('/api/sensors/readings-count/today');
    },
};
