class GaugeCard {
    #card = null;
    #gauge = null;
    #datetimeValue = null;
    #locales = null;
    #temperatureUnit = null;
    static #INVALID_READING = -404;

    constructor(element, sensorId, sensorName, temperatureUnit, minTemperature, maxTemperature) {
        this.#locales = getUserLocales();
        GaugeCard.#prepareCard(element, sensorId, sensorName);
        this.#card = element;
        this.#datetimeValue = element.querySelector('.datetime-value');
        this.#temperatureUnit = temperatureUnit;
        this.#gauge = new JustGage({
            id: this.#card.querySelector('.gauge').id,
            value: temperatureValue(minTemperature, temperatureUnit),
            min: temperatureValue(minTemperature, temperatureUnit),
            max: temperatureValue(maxTemperature, temperatureUnit),
            gaugeWidthScale: 0.75,
            textRenderer: (value) => {
                if (value === GaugeCard.#INVALID_READING) {
                    return 'N/A';
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

    getCardElement() {
        return this.#card;
    }

    setReading(reading) {
        this.#datetimeValue.textContent = formatDateToCompactDatetime(
            new Date(reading.created_on),
            this.#locales
        );

        const temperature = (reading.temperature !== null)
            ? reading.temperature
            : GaugeCard.#INVALID_READING;
        this.#gauge.refresh(temperature);
    }
}
