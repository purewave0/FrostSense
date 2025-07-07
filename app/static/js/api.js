const Api = {
    fetchSensors() {
        return fetch('/api/sensors');
    },

    fetchLatestSensorReadings() {
        return fetch('/api/readings/latest');
    },
};
