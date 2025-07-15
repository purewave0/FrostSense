document.addEventListener('DOMContentLoaded', async () => {
    const gaugeCardsDestination = document.getElementById('gauge-cards');

    const response = await Api.fetchSensors();
    const sensors = await response.json();

    Api.fetchLastSensorReadings()
        .then((response) => response.json())
        .then((sensorReadings) => {
            for (const sensor of sensors) {
                // would've used a DocumentFragment here, but JustGage needs the element
                // in the DOM already
                const card = document.createElement('div');
                gaugeCardsDestination.append(card);

                const gaugeCard = new GaugeCard(card, sensor.id, sensor.name);
                gaugeCard.setTemperature(sensorReadings[sensor.id].temperature);
            }

        });
});
