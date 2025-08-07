class GraphCard {
    #card = null;
    #data = [];
    #graph = null;
    #controls = null;
    #infoText = null;
    #readingsCountValue = null;
    #locales = [];

    constructor(element, sensorId, sensorName) {
        this.#locales = getUserLocales();
        GraphCard.#prepareCard(element, sensorId, sensorName);
        this.#card = element;
        this.#infoText = this.#card.querySelector('.info-text');
        this.#readingsCountValue = this.#card.querySelector('.readings-count-value');

        this.#controls = {
            'previousDayButton': this.#card.querySelector('.button-previous'),
            'currentDate': this.#card.querySelector('.current-date'),
            'nextDayButton': this.#card.querySelector('.button-next'),
        }

        this.#graph = new Dygraph(
            this.#card.querySelector('.graph'),
            [],  // empty data
            {
                interactionModel: {}, // disable zooming, etc.
                labels: null,  // we'll pass the proper values once the data is set
                valueRange: [-30, 30],
                legendFormatter: (data) => {
                    if (data.x == null) {
                        return '';  // no selection
                    }
                    const temperature = data.series[0].y.toFixed(1);
                    const datetime = formatDateToCompactDatetime(
                        new Date(data.x), this.#locales
                    );

                    return `
                        <b class="temperature-label">Temperature:</b>
                        <code>${temperature}</code> °C
                        <br>
                        at ${datetime}
                    `;
                },
                axes: {
                    y: {
                        valueFormatter(temperature) {
                            return formatTemperature(temperature)
                        },
                        axisLabelFormatter(temperature) {
                            return formatTemperature(temperature, 0);
                        },
                    },
                }
            }
        );
    }

    static #prepareCard(card, sensorId, sensorName) {
        card.dataset.sensorId = sensorId;
        card.className = 'graph-card';
        // TODO: svg icons for previous/next
        card.innerHTML = `
            <div class="header">
                <div class="sensor-name-wrapper">
                    <h2 class="sensor-name"></h2>
                </div>
                <div class="readings-count">
                    <span class="readings-count-value"></span> readings
                </div>
                <div class="controls">
                    <button class="button-previous">
                        <span>&lt;</span>
                    </button>
                    <input class="current-date" type="date">
                    <button class="button-next">
                        <span>&gt;</span>
                    </button>
                </div>
            </div>
            <div class="graph"></div>
            <p class="info-text"></p>
        `;

        const name = card.querySelector('.sensor-name');
        name.textContent = sensorName;
        name.title = sensorName;  // in case it gets ellipsized

        const graphElement = card.querySelector('.graph');
        graphElement.id = `graph${sensorId}`;
    }

    static #formatReadings(rawReadings) {
        // the format dygraphs expects is:
        // [
        //     [x,y,z], [x,y,z], [x,y,z]...
        // ] for data x, y, and z.
        return rawReadings.map((reading) => {
            return [new Date(reading.created_on), reading.temperature, reading.id]
        });
    }

    setReadings(readings) {
        let labels = null;
        if (readings.length > 0) {
            labels = ['Time', 'Temperature', 'id'];
            this.#card.classList.remove('empty');
        } else {
            // prevent "mismatch between number of labels and columns" error
            labels = null;
            this.#card.classList.add('empty');
        }
        this.#data = GraphCard.#formatReadings(readings)
        this.#graph.updateOptions({
            'labels': labels,
            'file': this.#data
        });
        this.#readingsCountValue.textContent = this.#data.length;
    }

    pushReadings(readings) {
        this.#data.push(...GraphCard.#formatReadings(readings));
        this.#graph.updateOptions({
            'labels': ['Time', 'Temperature', 'id'],
            'file': this.#data,
        });
        this.#readingsCountValue.textContent = this.#data.length;
    }

    getCardElement() {
        return this.#card;
    }

    getControls() {
        return this.#controls;
    }

    getCurrentDay() {
        return this.#controls.currentDate.valueAsDate;
    }

    getReadingsCount() {
        return this.#data.length;
    }

    setInfoTextHTML(html) {
        this.#infoText.innerHTML = html;
    }

    getLastReadingId() {
        return this.#data.at(-1)[2];
    }
}
