class GaugeCard {
    #card = null;
    #gauge = null;

    constructor(element, sensorId, sensorName) {
        GaugeCard.#prepareCard(element, sensorId, sensorName);
        this.#card = element;
        this.#gauge = new JustGage({
            id: this.#card.querySelector('.gauge').id,
            // TODO
            value: 0,
            min: -40,
            max: 40,
            textRenderer: (value) => {
                return `${value.toFixed(1)} °C`;
            },
        });
    }

    static #prepareCard(card, sensorId, sensorName) {
        card.dataset.sensorId = sensorId;
        card.className = 'gauge-card';
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

    setTemperature(temperature) {
        this.#gauge.refresh(temperature);
    }

}
