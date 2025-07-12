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

    fetchSensorReadingsInTimeRange(sensorId, rangeStart, rangeEnd) {
        return fetch(
            `/api/sensors/${sensorId}/readings-count`
            + `?range_start=${encodeURIComponent(rangeStart)}`
            + `&range_end=${encodeURIComponent(rangeEnd)}`
        );
    }
};
