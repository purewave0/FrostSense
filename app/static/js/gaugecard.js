class GaugeCard {
    #card = null;
    #gauge = null;

    constructor(element, sensorId, sensorName) {
        GaugeCard.#prepareCard(element, sensorId, sensorName);
        this.#card = element;
        this.#gauge = new JustGage({
            id: this.#card.querySelector('.gauge').id,
            value: 0,
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
            <h2 class='sensor-name'></h2>
            <div class='gauge'></div>
        `;

        const name = card.querySelector('.sensor-name');
        name.textContent = sensorName;

        const gaugeElement = card.querySelector('.gauge');
        gaugeElement.id = `gauge${sensorId}`;
        // gaugeElement.style.width = 64;
        // gaugeElement.style.height = 64;
    }

    getCardElement() {
        return this.#card;
    }

    // TODO: change to setReading(reading)
    setTemperature(temperature) {
        this.#gauge.refresh(temperature);
    }

}
