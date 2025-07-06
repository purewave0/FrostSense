function createSensorCard(sensor) {
    const card = document.createElement('div');
    card.className = 'sensor';
    card.innerHTML = `
        <h2 class="sensor-name"></h2>
    `;

    const sensorName = card.querySelector('.sensor-name');
    sensorName.textContent = sensor.name;

    return card;
}


document.addEventListener('DOMContentLoaded', () => {
    const sensorsDestination = document.getElementById('sensors');
    Api.fetchSensors()
        .then((response) => response.json())
        .then((sensors) => {
            const fragment = new DocumentFragment();
            for (const sensor of sensors) {
                const sensorCard = createSensorCard(sensor);
                fragment.append(sensorCard);
            }

            sensorsDestination.append(fragment);
        });
});
