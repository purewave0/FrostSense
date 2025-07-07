function createSensorReadingsCard(sensor, readings) {
    const card = document.createElement('div');
    card.dataset.sensorId = sensor.id;
    card.className = 'sensor-readings';
    card.innerHTML = `
        <h2 class="sensor-name"></h2>
        <ol class="readings"></ol>
    `;

    const sensorName = card.querySelector('.sensor-name');
    sensorName.textContent = sensor.name;

    // TODO: use a graph instead. this is just a prototype
    const readingsDestination = card.querySelector('.readings');
    const readingsFragment = new DocumentFragment();
    for (const reading of readings) {
        const readingItem = document.createElement('li');
        readingItem.textContent =
            `${roundTemperature(reading.temperature)} °C at ${reading.created_on}`;
        readingsFragment.append(readingItem);
    }
    readingsDestination.append(readingsFragment);

    return card;
}


document.addEventListener('DOMContentLoaded', async () => {
    const sensorReadingsDestination = document.getElementById('sensor-readings');

    const response = await Api.fetchSensors();
    const sensors = await response.json();

    Api.fetchLatestSensorReadings()
        .then((response) => response.json())
        .then((sensorReadings) => {
            const fragment = new DocumentFragment();

            for (const sensor of sensors) {
                const readings = sensorReadings[sensor.id];
                const card = createSensorReadingsCard(sensor, readings);
                fragment.append(card);
            }

            sensorReadingsDestination.append(fragment);
        });
});
