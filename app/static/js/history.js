document.addEventListener('DOMContentLoaded', async () => {
    const graphCardsDestination = document.getElementById('graph-cards');

    const response = await Api.fetchSensors();
    const sensors = await response.json();

    const graphCards = {};
    const readingsResponse = await Api.fetchSensorReadingsForDay(getStartOfToday());
    const sensorReadings = await readingsResponse.json();
    for (const sensor of sensors) {
        const card = document.createElement('div');
        graphCardsDestination.append(card);

        const graphCard = new GraphCard(card, sensor.id, sensor.name);
        graphCards[sensor.id] = graphCard;

        const controls = graphCard.getControls();
        controls.currentDate.valueAsDate = getStartOfToday();
        controls.currentDate.max = formatDateForDateInput(getStartOfToday());

        controls.currentDate.addEventListener('change', () => {
            // the currentDate's value needs to be adjusted for comparison, as it is in
            // the local timezone whereas getStartOfToday()'s result is in UTC
            const newDate = adjustToUTC(controls.currentDate.valueAsDate);
            if (newDate.getTime() === getStartOfToday().getTime()) {
                controls.nextDayButton.disabled = true;
            }
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
        const sensorIds = sensors.map((sensor) => sensor.id);
        const offsetIds = [];
        for (const sensorId of sensorIds) {
            const graphCard = graphCards[sensorId];
            if (graphCard.getReadingsCount() === 0) {
                offsetIds.push(0);  // there's nothing, so start from the beginning
            } else {
                offsetIds.push(graphCard.getLastReadingId());
            }
        }
        Api.fetchSensorReadingsForDay(getStartOfToday(), sensorIds, offsetIds)
            .then((response) => response.json())
            .then((sensorReadings) => {
                for (const sensor of sensors) {
                    const readings = sensorReadings[sensor.id];
                    if (readings.length === 0) {
                        continue;
                    }

                    graphCards[sensor.id].pushReadings(readings);
                }
            });
    }, UPDATE_INTERVAL);
});
