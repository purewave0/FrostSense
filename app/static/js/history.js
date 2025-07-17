document.addEventListener('DOMContentLoaded', async () => {
    const graphCardsDestination = document.getElementById('graph-cards');

    const response = await Api.fetchSensors();
    const sensors = await response.json();
    const sensorIds = sensors.map((sensor) => sensor.id);

    const graphCards = {};
    // initially, fetching today's readings for all of them
    const startDates = Array(sensors.length).fill(getStartOfToday());
    const readingsResponse = await Api.fetchSensorReadingsByDays(sensorIds, startDates);
    const sensorReadings = await readingsResponse.json();
    for (const sensor of sensors) {
        const card = document.createElement('div');
        graphCardsDestination.append(card);

        const graphCard = new GraphCard(card, sensor.id, sensor.name);
        graphCards[sensor.id] = graphCard;

        const controls = graphCard.getControls();
        controls.currentDate.valueAsDate = getStartOfToday();
        controls.currentDate.max = formatDateForDateInput(getStartOfToday());

        // TODO: cache 2-3 most recently fetched days?
        controls.currentDate.addEventListener('change', () => {
            // the currentDate's value needs to be adjusted, as it is in the local
            // timezone whereas getStartOfToday()'s result is in UTC
            const newDate = adjustToUTC(controls.currentDate.valueAsDate);
            if (newDate.getTime() === getStartOfToday().getTime()) {
                controls.nextDayButton.disabled = true;
            }

            Api.fetchSensorReadingsByDays([sensor.id], [newDate], null)
                .then((response) => response.json())
                .then((sensorReadings) => {
                    console.log(sensorReadings)
                    console.log(sensorReadings[sensor.id])
                    graphCard.setReadings(sensorReadings[sensor.id]);
                });
        })

        controls.previousDayButton.addEventListener('click', () => {
            controls.nextDayButton.disabled = false;
            const currentDate = controls.currentDate.valueAsDate;
            currentDate.setDate(currentDate.getDate() - 1);
            controls.currentDate.valueAsDate = currentDate;

            controls.currentDate.dispatchEvent(new Event('change'));
        });

        // no readings tomorrow yet, of course
        controls.nextDayButton.disabled = true;
        controls.nextDayButton.addEventListener('click', () => {
            const currentDate = controls.currentDate.valueAsDate;
            currentDate.setDate(currentDate.getDate() + 1);
            controls.currentDate.valueAsDate = currentDate;

            controls.currentDate.dispatchEvent(new Event('change'));
        });

        const readings = sensorReadings[sensor.id];
        if (readings.length > 0) {
            graphCard.setReadings(readings);
        }
    }

    setInterval(() => {
        const sensorIdsToUpdate = [];
        const startDates = [];
        const offsetIds = [];
        for (const sensorId of sensorIds) {
            const graphCard = graphCards[sensorId];
            const currentDate = adjustToUTC(graphCard.getCurrentDay());
            const isViewingTodaysReadings =
                currentDate.getTime() === getStartOfToday().getTime();
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
            .then((response) => response.json())
            .then((sensorReadings) => {
                for (const sensorId in sensorReadings) {
                    const readings = sensorReadings[sensorId];
                    if (readings.length === 0) {
                        continue;
                    }

                    graphCards[sensorId].pushReadings(readings);
                }
            });
    }, UPDATE_INTERVAL);
});
