document.addEventListener('DOMContentLoaded', async () => {
    const graphCardsDestination = document.getElementById('graph-cards');

    const response = await Api.fetchSensors();
    const sensors = await response.json();

    if (sensors.length === 0) {
        document.body.classList.remove('loading-graph-cards');
        document.body.classList.add('no-sensors');
        return;
    }

    const sensorIds = sensors.map((sensor) => sensor.id);

    const graphCards = {};
    // initially, fetching today's readings for all of them
    const startDates = Array(sensors.length).fill(getStartOfToday());
    const readingsResponse = await Api.fetchSensorReadingsByDays(sensorIds, startDates);
    const sensorReadings = await readingsResponse.json();

    const temperatureUnit = PreferencesCache.getTemperatureUnit();
    const temperatureLimits = SystemSettingsCache.getGraphLimits();
    const minTemperature = temperatureLimits.minimum;
    const maxTemperature = temperatureLimits.maximum;

    const bodyStyle = window.getComputedStyle(document.body);
    const graphLineColour = bodyStyle.getPropertyValue('--color-graph-line');

    const mediaQuery = window.matchMedia("screen and (max-width: 768px)");
    const isMobile = mediaQuery.matches;
    const MOBILE_GRAPH_WIDTH = 270;
    const MOBILE_GRAPH_HEIGHT = 300;

    for (const sensor of sensors) {
        const card = document.createElement('div');
        graphCardsDestination.append(card);

        const graphCard = new GraphCard(
            card,
            sensor.id,
            sensor.name,
            temperatureUnit,
            minTemperature,
            maxTemperature,
            graphLineColour,
            isMobile ? (MOBILE_GRAPH_WIDTH) : 480,
            isMobile ? (MOBILE_GRAPH_HEIGHT) : 320,
        );
        graphCards[sensor.id] = graphCard;
        graphCard.getCardElement().classList.add('today');

        const controls = graphCard.getControls();
        controls.currentDate.valueAsDate = getStartOfToday();
        controls.currentDate.max = formatDateForDateInput(getStartOfToday());

        // TODO: cache 2-3 most recently fetched days?
        controls.currentDate.addEventListener('change', () => {
            if (!controls.currentDate.checkValidity()) {
                graphCard.setReadings([]);
                graphCard.setInfoTextHTML('No readings');
                controls.currentDate.reportValidity();
                return;
            }
            // the currentDate's value needs to be adjusted, as it is in the local
            // timezone whereas getStartOfToday()'s result is in UTC
            const newDate = adjustToUTC(graphCard.getCurrentDay());

            const isToday = newDate.getTime() === getStartOfToday().getTime();
            if (isToday) {
                graphCard.getCardElement().classList.add('today');
                // can't see into the future!
                controls.nextDayButton.disabled = true;
            } else {
                graphCard.getCardElement().classList.remove('today');
                controls.nextDayButton.disabled = false;
            }

            Api.fetchSensorReadingsByDays([sensor.id], [newDate])
                .then((response) => {
                    if (response.ok) {
                        return response.json();
                    }
                    throw new Error();
                }).then((sensorReadings) => {
                    const readings = sensorReadings[sensor.id];
                    graphCard.setReadings(readings);
                    if (readings.length > 0) {
                        graphCard.setInfoTextHTML(
                            formattedTemperatureHTML(
                                sensorReadings[sensor.id].at(-1).temperature,
                                temperatureUnit
                            )
                        )
                    } else {
                        graphCard.setInfoTextHTML('No readings')
                    }
                }).catch(() => {
                    showToast(ToastType.ERROR, 'Failed to get readings for this day');
                });
        })

        controls.previousDayButton.addEventListener('click', () => {
            if (!controls.currentDate.checkValidity()) {
                controls.currentDate.reportValidity();
                return;
            }
            controls.nextDayButton.disabled = false;
            const currentDate = controls.currentDate.valueAsDate;
            currentDate.setDate(currentDate.getDate() - 1);
            controls.currentDate.valueAsDate = currentDate;

            controls.currentDate.dispatchEvent(new Event('change'));
        });

        // no readings tomorrow yet, of course
        controls.nextDayButton.disabled = true;
        controls.nextDayButton.addEventListener('click', () => {
            if (!controls.currentDate.checkValidity()) {
                controls.currentDate.reportValidity();
                return;
            }
            const currentDate = controls.currentDate.valueAsDate;
            currentDate.setDate(currentDate.getDate() + 1);
            controls.currentDate.valueAsDate = currentDate;

            controls.currentDate.dispatchEvent(new Event('change'));
        });

        const readings = sensorReadings[sensor.id];
        graphCard.setReadings(readings);
        if (readings.length > 0) {
            graphCard.setInfoTextHTML(
                formattedTemperatureHTML(
                    readings.at(-1).temperature, temperatureUnit
                )
            )
        } else {
            graphCard.setInfoTextHTML('No readings')
        }
    }

    document.body.classList.remove('loading-graph-cards');

    setInterval(() => {
        const sensorIdsToUpdate = [];
        const startDates = [];
        const offsetIds = [];
        for (const sensorId of sensorIds) {
            const graphCard = graphCards[sensorId];
            if (!graphCard.getControls().currentDate.checkValidity()) {
                graphCard.setReadings([]);
                graphCard.setInfoTextHTML('No readings');
                continue;
            }
            const adjustedDate = adjustToUTC(graphCard.getCurrentDay());
            const isViewingTodaysReadings =
                adjustedDate.getTime() === getStartOfToday().getTime();
            if (isViewingTodaysReadings) {
                // only today can new readings be available; past days are already
                // completed
                sensorIdsToUpdate.push(sensorId);
                if (graphCard.getReadingsCount() === 0) {
                    offsetIds.push(0);  // there's nothing, so start from the beginning
                } else {
                    offsetIds.push(graphCard.getLastReadingId());
                }
                startDates.push(getStartOfToday());
            }
        }
        if (sensorIdsToUpdate.length === 0) {
            // none of the sensors are viewing Today's readings
            return;
        }

        Api.fetchSensorReadingsByDays(sensorIdsToUpdate, startDates, offsetIds)
            .then((response) => {
                if (response.ok) {
                    return response.json();
                }
                throw new Error();
            }).then((sensorReadings) => {
                for (const sensorId in sensorReadings) {
                    const readings = sensorReadings[sensorId];
                    if (readings.length === 0) {
                        continue;
                    }

                    graphCards[sensorId].pushReadings(readings);
                    graphCards[sensorId].setInfoTextHTML(
                        formattedTemperatureHTML(
                            readings.at(-1).temperature, temperatureUnit
                        )
                    );
                }
            }).catch(() => {
                showToast(ToastType.ERROR, 'Failed to get new readings');
            });
    }, UPDATE_INTERVAL);
});
