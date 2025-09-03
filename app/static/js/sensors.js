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

    const optionsMenu = document.getElementById('sensor-options-menu');

    let currentlySelectedSensorCard = null;

    function areAnyModalsOpen() {
        return document.querySelector('.modal.is-open') !== null;
    }

    function menuOutsideClickHandler(event) {
        if (areAnyModalsOpen()) {
            // while modals are open, we must keep the menu open too so the sensor
            // remains 'selected'
            return;
        }
        if (!optionsMenu.contains(event.target)) {
            const sensorCurrentlyShowingOptions = sensorsDestination
                .querySelector('.showing-options');
            const menuButton =
                sensorCurrentlyShowingOptions.querySelector('.sensor-options-button');
            menuButton.dispatchEvent(new Event('click'));
        }
    }

    function menuEscHandler(event) {
        if (areAnyModalsOpen()) {
            return;
        }
        if (event.key === 'Escape') {
            const menuButton =
                currentlySelectedSensorCard.querySelector('.sensor-options-button');
            menuButton.dispatchEvent(new Event('click'));
        }
    }

    function showMenu(sensorCard) {
        const menuButton = sensorCard.querySelector('.sensor-options-button');
        FloatingUIDOM.computePosition(menuButton, optionsMenu, {
            placement: 'right-start',
            middleware: [
                FloatingUIDOM.offset(4),
                FloatingUIDOM.flip(),
                FloatingUIDOM.shift()
            ],
        }).then(({ x, y }) => {
            sensorCard.classList.add('showing-options');
            optionsMenu.classList.add('visible');
            Object.assign(optionsMenu.style, {
                left: `${x}px`,
                top: `${y}px`,
            });
            document.addEventListener('click', menuOutsideClickHandler);
            document.addEventListener('keydown', menuEscHandler);
            currentlySelectedSensorCard = sensorCard;
        });
    }

    function hideMenu() {
        if (currentlySelectedSensorCard) {
            currentlySelectedSensorCard.classList.remove('showing-options');
            currentlySelectedSensorCard = null;
        }
        optionsMenu.classList.remove('visible');
        document.removeEventListener('click', menuOutsideClickHandler);
        document.removeEventListener('keydown', menuEscHandler);
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
            hideMenu();
            if (!isThisShowingOptions) {
                // another card is currently showing its menu. show this one's
                // instead
                showMenu(sensorCard);
            }

            // prevent this click from insta-closing the dropdown
            event.stopPropagation();
        });
    }

    sensorsDestination.append(fragment);

    const createButton = document.getElementById('create-button');
    createButton.disabled = false;

    createButton.addEventListener('click', () => { alert('TODO') });

    const editOption = document.getElementById('option-edit');
    editOption.addEventListener('click', () => {
        alert('edit TODO');
    });


    const manageKeyOption = document.getElementById('option-manage-key');
    manageKeyOption.addEventListener('click', () => {
        alert('manageKey TODO');
    });

    const deleteModal = {
        'name': document.getElementById('modal-delete-name'),
        'createdOn': document.getElementById('modal-delete-created-on'),
        'deleteButton': document.getElementById('modal-delete-delete'),
    };
    deleteModal.deleteButton.addEventListener('click', () => {
        alert('TODO deleting sensor with id ' + currentlySelectedSensorCard.dataset.id);
        MicroModal.close('modal-delete');
        hideMenu();
    });

    function openDeleteModal(name, createdOn) {
        deleteModal.name.textContent = name;
        deleteModal.createdOn.textContent = formatDateToCompactDatetime(
            new Date(createdOn), locales
        );
        MicroModal.show('modal-delete');
    }

    const deleteOption = document.getElementById('option-delete');
    deleteOption.addEventListener('click', () => {
        const name = currentlySelectedSensorCard.dataset.name;
        const createdOn = new Date(currentlySelectedSensorCard.dataset.createdOn);
        openDeleteModal(name, createdOn);
    });
});
