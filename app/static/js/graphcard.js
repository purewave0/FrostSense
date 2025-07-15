class GraphCard {
    #card = null;
    #data = [];
    #graph = null;
    // TODO: make this configurable; or, instead, show readings *per day*?
    static #MAX_READINGS = 40;

    constructor(element, sensorId, sensorName) {
        GraphCard.#prepareCard(element, sensorId, sensorName);
        this.#card = element;
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
        card.innerHTML = `
            <h2 class='sensor-name'></h2>
            <div class='graph'></div>
        `;

        const name = card.querySelector('.sensor-name');
        name.textContent = sensorName;

        const graphElement = card.querySelector('.graph');
        graphElement.id = `graph${sensorId}`;
    }

    setReadings(readings) {
        // the format dygraphs expects is:
        // [
        //     [x,y], [x,y], [x,y]...
        // ] for data x and y.
        const formattedReadings =
            readings.map((reading) => {
                return [new Date(reading.created_on), reading.temperature, reading.id]
            });
        this.#data = formattedReadings;
        this.#graph.updateOptions({
            'labels': ['Time', 'Temperature', 'id'],
            'file': formattedReadings
        });
    }

    addReadings(readings) {
        this.#data.push(...readings);
        const excess = this.#data.length - GraphCard.#MAX_READINGS;
        if (excess > 0) {
            this.#data.slice(excess);
        }
        this.#graph.updateOptions({ 'file': this.#data });
    }

    getCardElement() {
        return this.#card;
    }
}
