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
        graphCard.setReadings(sensorReadings[sensor.id]);
        graphCards[sensor.id] = graphCard;
    }
});
