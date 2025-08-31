class GraphCard {
    #card = null;
    #data = [];
    #graph = null;
    #controls = null;
    #infoText = null;
    #readingsCountValue = null;
    #locales = [];
    #temperatureUnit = null;

    constructor(element, sensorId, sensorName, temperatureUnit, minTemperature, maxTemperature) {
        this.#locales = getUserLocales();
        GraphCard.#prepareCard(element, sensorId, sensorName);
        this.#card = element;
        this.#infoText = this.#card.querySelector('.info-text');
        this.#readingsCountValue = this.#card.querySelector('.readings-count-value');
        this.#temperatureUnit = temperatureUnit;

        this.#controls = {
            'previousDayButton': this.#card.querySelector('.button-previous'),
            'currentDate': this.#card.querySelector('.current-date'),
            'nextDayButton': this.#card.querySelector('.button-next'),
        }

        const unitString = TemperatureUnitStrings[temperatureUnit];

        this.#graph = new Dygraph(
            this.#card.querySelector('.graph'),
            [],  // empty data
            {
                interactionModel: {}, // disable zooming, etc.
                labels: null,  // we'll pass the proper values once the data is set
                valueRange: [
                    temperatureValue(minTemperature, temperatureUnit),
                    temperatureValue(maxTemperature, temperatureUnit)
                ],
                legendFormatter: (data) => {
                    if (data.x == null) {
                        return '';  // no selection
                    }
                    // temperature already in the proper unit
                    const temperature = data.series[0].y.toFixed(1);
                    const datetime = formatDateToCompactDatetime(
                        new Date(data.x), this.#locales
                    );

                    return `
                        <b class="temperature-label">Temperature:</b>
                        <code>${temperature}</code> ${unitString}
                        <br>
                        at ${datetime}
                    `;
                },
                axes: {
                    y: {
                        axisLabelFormatter: (temperature) => {
                            // temperature already in the proper unit
                            return `${temperature} ${unitString}`;
                        },
                    },
                }
            }
        );
    }

    static #prepareCard(card, sensorId, sensorName) {
        card.dataset.sensorId = sensorId;
        card.className = 'graph-card';
        card.innerHTML = `
            <div class="header">
                <div class="sensor-name-wrapper">
                    <h2 class="sensor-name"></h2>
                </div>
                <div class="readings-count">
                    <span class="readings-count-value"></span> readings
                </div>
                <div class="controls">
                    <button class="button-previous" title="Previous day">
                        <svg xmlns="http://www.w3.org/2000/svg"
                            height="24px"
                            viewBox="0 -960 960 960"
                            width="24px"
                            fill="#e3e3e3">
                            <path d="M560-240 320-480l240-240 56 56-184 184 184 184-56 56Z"/>
                        </svg>
                    </button>
                    <input class="current-date" type="date">
                    <button class="button-next" title="Next day">
                        <svg xmlns="http://www.w3.org/2000/svg"
                            height="24px"
                            viewBox="0 -960 960 960"
                            width="24px" fill="#e3e3e3">
                            <path d="M504-480 320-664l56-56 240 240-240 240-56-56 184-184Z"/>
                        </svg>
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

    static #formatAndConvertReadings(rawReadings, temperatureUnit) {
        // the format dygraphs expects is:
        // [
        //     [x,y,z], [x,y,z], [x,y,z]...
        // ] for data x, y, and z.
        return rawReadings.map((reading) => {
            return [
                new Date(reading.created_on),
                temperatureValue(reading.temperature, temperatureUnit),
                reading.id
            ]
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
        this.#data =
            GraphCard.#formatAndConvertReadings(readings, this.#temperatureUnit)
        this.#graph.updateOptions({
            'labels': labels,
            'file': this.#data
        });
        this.#readingsCountValue.textContent = this.#data.length;
    }

    pushReadings(readings) {
        this.#data.push(
            ...GraphCard.#formatAndConvertReadings(
                readings, this.#temperatureUnit
            )
        );
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
