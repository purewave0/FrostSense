class GaugeCard {
    #card = null;
    #gauge = null;
    #datetimeValue = null;
    #locales = null;
    static #INVALID_TEMPERATURE = -404;
    static #NO_READING = -505;

    /**
     * Create a new GaugeCard.
     *
     * @param {Node} element The element for displaying the gauge.
     * @param {number} sensorId The ID of the sensor the readings belong to.
     * @param {string} sensorName The name of the sensor the readings belong to.
     * @param {string} temperatureUnit The unit for displaying temperatures.
     * @param {number} minTemperature The lowest value this gauge can show, in Celsius.
     * @param {number} maxTemperature The highest value this gauge can show, in Celsius.
     */
    constructor(
        element, sensorId, sensorName, temperatureUnit, minTemperature, maxTemperature
    ) {
        this.#locales = getUserLocales();
        GaugeCard.#prepareCard(element, sensorId, sensorName);
        this.#card = element;
        this.#datetimeValue = element.querySelector('.datetime-value');
        this.#gauge = new JustGage({
            id: this.#card.querySelector('.gauge').id,
            value: temperatureValue(minTemperature, temperatureUnit),
            min: temperatureValue(minTemperature, temperatureUnit),
            max: temperatureValue(maxTemperature, temperatureUnit),
            gaugeWidthScale: 0.75,
            textRenderer: (value) => {
                if (value === GaugeCard.#INVALID_TEMPERATURE) {
                    return 'N/A';
                } else if (value === GaugeCard.#NO_READING) {
                    return 'Empty';
                }
                return formattedTemperature(value, temperatureUnit);
            },
            startAnimationTime: 500,
            refreshAnimationTime: 500,
            pointer: true,
            pointerOptions: {
                toplength: 16,
                bottomlength: 24,
                bottomwidth: 8,
            },
            hideMinMax: true,
        });
    }

    /**
     * Prepare the given `card` element with the given sensor ID and name.
     */
    static #prepareCard(card, sensorId, sensorName) {
        card.dataset.sensorId = sensorId;
        card.className = 'gauge-card';
        card.innerHTML = `
            <div class="header">
                <h2 class="sensor-name"></h2>
                <div class="datetime-value"></div>
            </div>
            <div class="gauge"></div>
        `;

        const datetimeValue = card.querySelector('.datetime-value');
        datetimeValue.textContent = 'N/A';

        const name = card.querySelector('.sensor-name');
        name.textContent = sensorName;
        name.title = sensorName;  // in case it gets ellipsized

        const gaugeElement = card.querySelector('.gauge');
        gaugeElement.id = `gauge${sensorId}`;
    }

    /**
     * Return the underlying card element for this gauge card.
     */
    getCardElement() {
        return this.#card;
    }

    /**
     * Display the given reading. If `null`, display an "Empty" text.
     *
     * @param {object?} reading The reading object returned by the API, containing `id`
     *     (unused), `temperature` in Celsius and `created_on`. If `temperature` is
     *     `null`, display a "N/A" text indicating the temperature is invalid.
     */
    setReading(reading) {
        if (reading === null) {
            this.#datetimeValue.textContent = '';
            this.#gauge.refresh(GaugeCard.#NO_READING);
            return;
        }

        this.#datetimeValue.textContent = formatDateToCompactDatetime(
            new Date(reading.created_on),
            this.#locales
        );

        const temperature = (reading.temperature !== null)
            ? reading.temperature
            : GaugeCard.#INVALID_TEMPERATURE;
        this.#gauge.refresh(temperature);
    }
}
