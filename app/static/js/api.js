const Api = {
    fetchSensors() {
        return fetch('/api/sensors');
    },

    fetchLatestSensorReadings() {
        return fetch('/api/readings/latest');
    },

    fetchTodayReadingsCounts() {
        return fetch('/api/sensors/readings-count/today');
    },
};
