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
    }
};
