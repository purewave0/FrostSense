function getStartOfToday() {
    const start = new Date();
    start.setHours(0, 0, 0, 0);  // hours, minutes, seconds, millis

    return start;
}


document.addEventListener('DOMContentLoaded', async () => {
    const graphCardsDestination = document.getElementById('graph-cards');

    const response = await Api.fetchSensors();
    const sensors = await response.json();

    const graphCards = {};
    const readingsResponse = await Api.fetchSensorReadingsForDay(getStartOfToday());
    const sensorReadings = await readingsResponse.json();
    for (const sensor of sensors) {
        const card = document.createElement('div');
        graphCardsDestination.append(card);

        const graphCard = new GraphCard(card, sensor.id, sensor.name);
        graphCards[sensor.id] = graphCard;
        const readings = sensorReadings[sensor.id];
        if (readings.length > 0) {
            graphCard.setReadings(readings);
        }
    }

    setInterval(() => {
        const sensorIds = sensors.map((sensor) => sensor.id);
        const offsetIds = [];
        for (const sensorId of sensorIds) {
            const graphCard = graphCards[sensorId];
            if (graphCard.getReadingsCount() === 0) {
                offsetIds.push(0);  // there's nothing, so start from the beginning
            } else {
                offsetIds.push(graphCard.getLastReadingId());
            }
        }
        Api.fetchSensorReadingsForDay(getStartOfToday(), sensorIds, offsetIds)
            .then((response) => response.json())
            .then((sensorReadings) => {
                for (const sensor of sensors) {
                    const readings = sensorReadings[sensor.id];
                    if (readings.length === 0) {
                        continue;
                    }

                    graphCards[sensor.id].pushReadings(readings);
                }
            });
    }, UPDATE_INTERVAL);
});
