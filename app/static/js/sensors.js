function createSensorCard(sensor, todayReadingsCount) {
    const card = document.createElement('div');
    card.className = 'sensor';
    card.innerHTML = `
        <h2 class="sensor-name"></h2>
        <p class="sensor-info"></p>
    `;

    const sensorName = card.querySelector('.sensor-name');
    sensorName.textContent = sensor.name;

    const sensorInfo = card.querySelector('.sensor-info');
    sensorInfo.textContent = `
        created on ${sensor.created_on};
        ${todayReadingsCount} readings today
    `;

    return card;
}


document.addEventListener('DOMContentLoaded', async () => {
    const sensorsDestination = document.getElementById('sensors');

    const sensorsResponse = await Api.fetchSensors();
    const sensors = await sensorsResponse.json();

    const todayCountsResponse = await Api.fetchTodayReadingsCounts();
    const todayCounts = await todayCountsResponse.json();

    const fragment = new DocumentFragment();
    for (const sensor of sensors) {
        const sensorId = sensor.id;
        const sensorCard = createSensorCard(sensor, todayCounts[sensorId]);
        fragment.append(sensorCard);
    }

    sensorsDestination.append(fragment);
});
