const Api = {
    fetchSensors() {
        return fetch('/api/sensors');
    },

    fetchLastSensorReadings() {
        return fetch('/api/sensors/last-readings');
    },

    fetchSensorReadingsForDay(startOfDay) {
        return fetch(
            '/api/sensors/readings/day/'
            + encodeURIComponent(startOfDay.toISOString())
        );
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
