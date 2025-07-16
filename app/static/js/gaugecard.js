class GaugeCard {
    #card = null;
    #gauge = null;
    #datetimeValue = null;
    #locales = null;

    constructor(element, sensorId, sensorName) {
        this.#locales = GaugeCard.#getUserLocales();
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

    static #getUserLocales() {
        return navigator.languages;
    }

    static #formatDate(date, locales) {
        return new Date(date).toLocaleString(
            locales,
            {
                'day': '2-digit',
                'month': '2-digit',
                'year': '2-digit',

                'hour': '2-digit',
                'minute': '2-digit',
            }
        );
    }

    setReading(reading) {
        this.#gauge.refresh(reading.temperature);
        this.#datetimeValue.textContent =
            GaugeCard.#formatDate(reading.created_on, this.#locales);
    }

}
