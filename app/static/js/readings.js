document.addEventListener('DOMContentLoaded', async () => {
    const gaugeCardsDestination = document.getElementById('gauge-cards');

    const sensorsResponse = await Api.fetchSensors();
    const sensors = await sensorsResponse.json();

    const gaugeCards = {};
    const readingsResponse = await Api.fetchLastSensorReadings();
    const sensorReadings = await readingsResponse.json();
    for (const sensor of sensors) {
        // would've used a DocumentFragment here, but JustGage needs the element
        // in the DOM already
        const card = document.createElement('div');
        gaugeCardsDestination.append(card);

        const gaugeCard = new GaugeCard(card, sensor.id, sensor.name);
        gaugeCards[sensor.id] = gaugeCard;
        gaugeCard.setTemperature(sensorReadings[sensor.id].temperature);
    }

    // TODO: tiny 'fetching readings' notification
    // TODO: handle errors
    setInterval(() => {
        Api.fetchLastSensorReadings()
            .then((response) => response.json())
            .then((sensorReadings) => {
                for (const sensor of sensors) {
                    gaugeCards[sensor.id].setTemperature(
                        sensorReadings[sensor.id].temperature
                    );
                }
            });
    }, UPDATE_INTERVAL)
});
