document.addEventListener('DOMContentLoaded', async () => {
    const graphCardsDestination = document.getElementById('graph-cards');

    const response = await Api.fetchSensors();
    const sensors = await response.json();

    Api.fetchLatestSensorReadings()
        .then((response) => response.json())
        .then((sensorReadings) => {
            for (const sensor of sensors) {
                const card = document.createElement('div');
                graphCardsDestination.append(card);

                const graphCard = new GraphCard(card, sensor.id, sensor.name);
                graphCard.setReadings(sensorReadings[sensor.id]);
            }
        });
});
