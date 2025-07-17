class GraphCard {
    #card = null;
    #data = [];
    #graph = null;
    #controls = null;

    constructor(element, sensorId, sensorName) {
        GraphCard.#prepareCard(element, sensorId, sensorName);
        this.#card = element;

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
                // we'll pass the labels once the data is set
                valueRange: [-30, 30],
                legendFormatter(data) {
                    if (data.x == null) {
                        return '';  // no selection
                    }
                    const temperature = data.series[0].y.toFixed(1);
                    // TODO: shorter format?
                    const datetime = new Date(data.x).toLocaleString();
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
                            return `${temperature.toFixed(1)} °C`;
                        },
                        axisLabelFormatter(temperature) {
                            return `${temperature.toFixed(0)} °C`;
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
                <h2 class="sensor-name"></h2>
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
        `;

        const name = card.querySelector('.sensor-name');
        name.textContent = sensorName;

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
        this.#data = GraphCard.#formatReadings(readings)
        this.#graph.updateOptions({
            'labels': ['Time', 'Temperature', 'id'],
            'file': this.#data
        });
    }

    pushReadings(readings) {
        this.#data.push(...GraphCard.#formatReadings(readings));
        this.#graph.updateOptions({
            'labels': ['Time', 'Temperature', 'id'],
            'file': this.#data,
        });
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

    getLastReadingId() {
        return this.#data.at(-1)[2];
    }
}
