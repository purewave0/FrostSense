function createSensorCard(sensor, todayReadingsCount, locales) {
    const card = document.createElement('div');
    card.className = 'sensor';
    card.innerHTML = `
        <div class="sensor-header">
            <div class="sensor-name-wrapper">
                <h2 class="sensor-name"></h2>
            </div>
            <button type="button" class="sensor-options-button" title="Options">
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    height="24px"
                    viewBox="0 -960 960 960"
                    width="24px"
                    fill="#e3e3e3"
                >
                    <path d="M480-160q-33 0-56.5-23.5T400-240q0-33 23.5-56.5T480-320q33 0 56.5 23.5T560-240q0 33-23.5 56.5T480-160Zm0-240q-33 0-56.5-23.5T400-480q0-33 23.5-56.5T480-560q33 0 56.5 23.5T560-480q0 33-23.5 56.5T480-400Zm0-240q-33 0-56.5-23.5T400-720q0-33 23.5-56.5T480-800q33 0 56.5 23.5T560-720q0 33-23.5 56.5T480-640Z"/>
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

    const todayCountsResponse = await Api.fetchTodayReadingsCounts();
    const todayCounts = await todayCountsResponse.json();

    const locales = getUserLocales();

    // TODO: rename 'tooltip' to 'menu'
    const optionsTooltip = document.getElementById('sensor-options-tooltip');

    function tooltipOutsideClickHandler(event) {
        if (!optionsTooltip.contains(event.target)) {
            const sensorCurrentlyShowingOptions = sensorsDestination
                .querySelector('.showing-options');
            const tooltipButton =
                sensorCurrentlyShowingOptions.querySelector('.sensor-options-button');
            tooltipButton.dispatchEvent(new Event('click'));
        }
    }

    function tooltipEscHandler(event) {
        if (event.key === 'Escape') {
            const sensorCurrentlyShowingOptions = sensorsDestination
                .querySelector('.showing-options');
            const tooltipButton =
                sensorCurrentlyShowingOptions.querySelector('.sensor-options-button');
            tooltipButton.dispatchEvent(new Event('click'));
        }
    }

    function showTooltip(sensorCard) {
        const optionsButton = sensorCard.querySelector('.sensor-options-button');
        FloatingUIDOM.computePosition(optionsButton, optionsTooltip, {
            placement: 'right-start',
            middleware: [
                FloatingUIDOM.offset(4),
                FloatingUIDOM.flip(),
                FloatingUIDOM.shift()
            ],
        }).then(({ x, y }) => {
            sensorCard.classList.add('showing-options');
            optionsTooltip.classList.add('visible');
            Object.assign(optionsTooltip.style, {
                left: `${x}px`,
                top: `${y}px`,
            });
            document.body.addEventListener('click', tooltipOutsideClickHandler);
            document.body.addEventListener('keydown', tooltipEscHandler);
        });
    }

    function hideTooltip() {
        const sensorCurrentlyShowingOptions = sensorsDestination
            .querySelector('.showing-options');
        if (sensorCurrentlyShowingOptions) {
            sensorCurrentlyShowingOptions.classList.remove('showing-options');
        }
        optionsTooltip.classList.remove('visible');
        document.body.removeEventListener('click', tooltipOutsideClickHandler);
        document.body.removeEventListener('keydown', tooltipEscHandler);
    }

    const fragment = new DocumentFragment();
    for (const sensor of sensors) {
        const sensorId = sensor.id;
        const sensorCard = createSensorCard(sensor, todayCounts[sensorId], locales);
        fragment.append(sensorCard);

        const optionsButton = sensorCard.querySelector('.sensor-options-button');
        optionsButton.addEventListener('click', (event) => {
            const isThisShowingOptions =
                sensorCard.classList.contains('showing-options');
            hideTooltip();
            if (!isThisShowingOptions) {
                // another card is currently showing options. change to this one
                showTooltip(sensorCard);
            }

            // prevent this click from insta-closing the dropdown
            event.stopPropagation();
        });
    }

    sensorsDestination.append(fragment);

    const createButton = document.getElementById('create-button');
    createButton.disabled = false;

    createButton.addEventListener('click', () => { alert('TODO') });
});
