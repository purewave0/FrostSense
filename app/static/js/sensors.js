function createSensorCard(sensor, todayReadingsCount, locales) {
    const card = document.createElement('div');
    card.className = 'sensor';
    card.innerHTML = `
        <div class="sensor-header">
            <div class="sensor-name-wrapper">
                <h2 class="sensor-name"></h2>
            </div>
            <div class="sensor-status active"></div>
        </div>
        <ul class="sensor-info">
            <li>
                Created on: <span class="created-on"></span>
            </li>
            <li>
                Readings today: <span class="readings-today"></span>
            </li>
        </ul>
    `;

    const sensorName = card.querySelector('.sensor-name');
    sensorName.textContent = sensor.name;
    sensorName.title = sensor.name;  // in case it gets ellipsized

    const createdOnValue = card.querySelector('.created-on');
    createdOnValue.textContent = formatDateToCompactDatetime(
        new Date(sensor.created_on), locales
    );
    const readingsTodayValue = card.querySelector('.readings-today');
    readingsTodayValue.textContent = todayReadingsCount;

    return card;
}


document.addEventListener('DOMContentLoaded', async () => {
    const sensorsDestination = document.getElementById('sensors');

    const sensorsResponse = await Api.fetchSensors();
    const sensors = await sensorsResponse.json();

    const todayCountsResponse = await Api.fetchTodayReadingsCounts();
    const todayCounts = await todayCountsResponse.json();

    const locales = getUserLocales();

    const fragment = new DocumentFragment();
    for (const sensor of sensors) {
        const sensorId = sensor.id;
        const sensorCard = createSensorCard(sensor, todayCounts[sensorId], locales);
        fragment.append(sensorCard);
    }

    sensorsDestination.append(fragment);

    const createButton = document.getElementById('create-button');
    createButton.disabled = false;

    createButton.addEventListener('click', () => { alert('TODO') })
});
