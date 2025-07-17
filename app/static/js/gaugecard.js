class GaugeCard {
    #card = null;
    #gauge = null;
    #datetimeValue = null;
    #locales = null;

    constructor(element, sensorId, sensorName) {
        this.#locales = getUserLocales();
        GaugeCard.#prepareCard(element, sensorId, sensorName);
        this.#card = element;
        this.#datetimeValue = element.querySelector('.datetime-value');
        this.#gauge = new JustGage({
            id: this.#card.querySelector('.gauge').id,
            value: -30,
            min: -30,
            minTxt: '-30 °C',
            max: 30,
            minTxt: '30 °C',
            gaugeWidthScale: 0.75,
            textRenderer: (value) => {
                if (value === null) {
                    // TODO: hide coloured value section (currently, it sits at 0)
                    return 'N/A';
                }
                return `${value.toFixed(1)} °C`;
            },
            startAnimationTime: 500,
            refreshAnimationTime: 500,
            pointer: true,
            pointerOptions: {
                toplength: 16,
                bottomlength: 24,
                bottomwidth: 8,
            }
        });
    }

    static #prepareCard(card, sensorId, sensorName) {
        card.dataset.sensorId = sensorId;
        card.className = 'gauge-card';
        // TODO: datetime (of the current reading)
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

        const gaugeElement = card.querySelector('.gauge');
        gaugeElement.id = `gauge${sensorId}`;
    }

    getCardElement() {
        return this.#card;
    }

    setReading(reading) {
        if (reading === null) {
            this.#gauge.refresh(null);
            this.#datetimeValue.textContent = 'N/A';
            return;
        }
        this.#gauge.refresh(reading.temperature);
        this.#datetimeValue.textContent = formatDateToCompactDatetime(
            new Date(reading.created_on),
            this.#locales
        );
    }

}
