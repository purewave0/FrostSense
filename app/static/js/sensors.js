function createSensorCard(sensor, todayReadingsCount, locales) {
    const card = document.createElement('div');
    card.className = 'sensor';
    card.dataset.id = sensor.id;
    card.dataset.name = sensor.name;
    card.dataset.createdOn = sensor.created_on;
    card.innerHTML = `
        <div class="sensor-header">
            <div class="sensor-name-wrapper">
                <h2 class="sensor-name"></h2>
            </div>
            <button type="button" class="sensor-edit-button" title="Edit">
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    height="24px"
                    viewBox="0 -960 960 960"
                    width="24px"
                    fill="#e3e3e3"
                >
                    <path d="M200-200h57l391-391-57-57-391 391v57Zm-80 80v-170l528-527q12-11 26.5-17t30.5-6q16 0 31 6t26 18l55 56q12 11 17.5 26t5.5 30q0 16-5.5 30.5T817-647L290-120H120Zm640-584-56-56 56 56Zm-141 85-28-29 57 57-29-28Z"/>
                </svg>
            </button>
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
    const sensorCards = [];

    const todayCountsResponse = await Api.fetchTodayReadingsCounts();
    const todayCounts = await todayCountsResponse.json();

    const locales = getUserLocales();

    let selectedSensor = null;

    const fragment = new DocumentFragment();
    for (const sensor of sensors) {
        const sensorCard = createSensorCard(sensor, todayCounts[sensor.id], locales);
        fragment.append(sensorCard);
        sensorCards.push(sensorCard);

        const editButton = sensorCard.querySelector('.sensor-edit-button');
        editButton.addEventListener('click', (event) => {
            selectedSensor = sensor;
            openEditModal(sensor.name)
        });
    }

    sensorsDestination.append(fragment);

    // -- edit modal --

    const editModal = {
        'form': document.getElementById('modal-edit-form'),
        'name': document.getElementById('modal-edit-name'),
    };
    editModal.form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const name = editModal.name.value.trim();
        await Api.editSensor(selectedSensor.id, name);
        // TODO: handle errors

        const correspondingSensorCard = sensorCards
            .find(card => Number(card.dataset.id) === selectedSensor.id);
        correspondingSensorCard.dataset.name = name;
        const nameElement = correspondingSensorCard.querySelector('.sensor-name');
        nameElement.textContent = name;
        MicroModal.close('modal-edit');
    });

    function openEditModal(name) {
        editModal.name.value = name;
        editModal.name.placeholder = name;
        MicroModal.show('modal-edit');
    }
});
