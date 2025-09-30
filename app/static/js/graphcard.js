class GraphCard {
    #card = null;
    #data = [];
    #graph = null;
    #controls = null;
    #infoText = null;
    #readingsCountValue = null;
    #locales = [];
    #temperatureUnit = null;
    static #TEMPERATURE_INDEX = 0;
    static #ID_INDEX = 2;

    /**
     * Create a new GraphCard.
     *
     * @param {Node} element The element for displaying the graph.
     * @param {number} sensorId The ID of the sensor the readings belong to.
     * @param {string} sensorName The name of the sensor the readings belong to.
     * @param {string} temperatureUnit The unit for displaying temperatures.
     * @param {number} minTemperature The lowest value this graph can show, in Celsius.
     * @param {number} maxTemperature The highest value this graph can show, in Celsius.
     * @param {string} lineColour The colour (hex, rgb, etc.) for the temperature line.
     * @param {number} [width=480] The graph width.
     * @param {number} [height=320] The graph height.
     */
    constructor(
        element,
        sensorId,
        sensorName,
        temperatureUnit,
        minTemperature,
        maxTemperature,
        lineColour,
        width = 480,
        height = 320
    ) {
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
        };

        const unitString = TemperatureUnitString[temperatureUnit];

        this.#graph = new Dygraph(
            this.#card.querySelector('.graph'),
            [],  // empty data
            {
                width: width,
                height: height,
                color: lineColour,
                strokeWidth: 1.5,
                visibility: [true, false],  // don't plot IDs
                interactionModel: {},  // disable zooming, etc.
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
                    const temperature =
                        data.series[GraphCard.#TEMPERATURE_INDEX].y.toFixed(1);
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

    /**
     * Prepare the given `card` element with the given sensor ID and name.
     */
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
                    <input class="current-date" type="date" required>
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

    /**
     * Return the given raw readings converted to Dygraphs' accepted format, which is
     * an array containing *each reading as an array of* [id, temperature, created_on].
     *
     * @param {object[]} rawReadings An array of reading objects (id, temperature,
     *     created_on).
     * @param {string} temperatureUnit The unit to convert the temperature values to.
     */
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

    /**
     * Clear all readings and display the given ones.
     *
     * @param {object[]} readings An array of reading objects (id, temperature,
     *     created_on).
     */
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

    /**
     * Add the given readings to the graph.
     *
     * @param {object[]} readings An array of reading objects (id, temperature,
     *     created_on).
     */
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

    /**
     * Return the underlying card element for this graph card.
     */
    getCardElement() {
        return this.#card;
    }

    /**
     * Return an object containing the current date input, and the previous day and next
     * day buttons.
     */
    getControls() {
        return this.#controls;
    }

    /**
     * Return the Date value of the current date input.
     */
    getCurrentDay() {
        return this.#controls.currentDate.valueAsDate;
    }

    /**
     * Return the number of readings being displayed.
     */
    getReadingsCount() {
        return this.#data.length;
    }

    /**
     * Set the HTML of the info text.
     *
     * Note: this is **raw** HTML; make sure it's safe!
     */
    setInfoTextHTML(html) {
        this.#infoText.innerHTML = html;
    }

    /**
     * Return the ID of the last (most recent) reading being displayed.
     */
    getLastReadingId() {
        return this.#data.at(-1)[GraphCard.#ID_INDEX];
    }
}
