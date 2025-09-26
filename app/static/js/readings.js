document.addEventListener('DOMContentLoaded', async () => {
    const gaugeCardsDestination = document.getElementById('gauge-cards');

    const sensorsResponse = await Api.fetchSensors();
    const sensors = await sensorsResponse.json();

    if (sensors.length === 0) {
        document.body.classList.remove('loading-gauge-cards');
        document.body.classList.add('no-sensors');
        return;
    }

    const gaugeCards = {};
    const readingsResponse = await Api.fetchLastSensorReadings();
    const sensorReadings = await readingsResponse.json();

    const temperatureUnit = PreferencesCache.getTemperatureUnit();
    const temperatureLimits = SystemSettingsCache.getGaugeLimits();
    const minTemperature = temperatureLimits.minimum;
    const maxTemperature = temperatureLimits.maximum;

    for (const sensor of sensors) {
        // would've used a DocumentFragment here, but JustGage needs the element
        // in the DOM already
        const card = document.createElement('div');
        gaugeCardsDestination.append(card);

        const gaugeCard = new GaugeCard(
            card, sensor.id, sensor.name, temperatureUnit, minTemperature, maxTemperature
        );
        gaugeCards[sensor.id] = gaugeCard;
        gaugeCard.setReading(sensorReadings[sensor.id]);
    }

    document.body.classList.remove('loading-gauge-cards');

    // TODO: tiny 'fetching readings' notification
    // TODO: handle errors
    setInterval(() => {
        Api.fetchLastSensorReadings()
            .then((response) => {
                if (response.ok) {
                    return response.json();
                }
                throw new Error();
            }).then((sensorReadings) => {
                for (const sensor of sensors) {
                    gaugeCards[sensor.id].setReading(sensorReadings[sensor.id]);
                }
            }).catch(() => {
                showToast(ToastType.ERROR, 'Failed to get new readings');
            });
    }, UPDATE_INTERVAL);
});
