function formatReadingsForGraph(rawReadings) {
    // the format dygraphs expects is:
    // [
    //     [x,y], [x,y], [x,y]...
    // ] for data x and y.
    return rawReadings.map((reading) => {
        return [new Date(reading.created_on), reading.temperature]
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const locales = getUserLocales();
    if (hasTable) {
        const rowsPerTable = 55;
        let rowIndex = 0;
        const tables = [];
        // use the horizontal space by distributing readings between multiple tables.
        // this avoids creating multiple pages unnecessarily
        for (const reading of readings) {
            const shouldCreateTable = rowIndex % rowsPerTable === 0;
            if (shouldCreateTable) {
                const table = document.createElement('table');
                table.className = 'table';
                tables.push(table);
            }

            const currentTable = tables.at(-1);

            const shouldAddHeader = rowIndex === 0;
            if (shouldAddHeader) {
                const headerRow = document.createElement('tr');
                headerRow.id = 'table-header';
                headerRow.innerHTML = `
                    <td>Time</td>
                    <td>°C</td>
                `;
                currentTable.append(headerRow);
                // it's a row too - count it
                ++rowIndex;
            }

            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="datetime"></td>
                <td class="temperature">°C</td>
            `;
            let formattedDatetime = formatDateToCompactDatetime(
                new Date(reading.created_on), locales
            ).replace(',', '');
            row.querySelector('.datetime').textContent = formattedDatetime;
            row.querySelector('.temperature').textContent =
                reading.temperature.toFixed(1);
            currentTable.append(row);
            ++rowIndex;
        }

        const tablesDestination = document.getElementById('tables-section');
        tablesDestination.append(...tables);
    }

    if (hasGraph) {
        const graphElement = document.getElementById('graph-section');

        let width = null;
        let height = null;
        if (hasTable) {
            // 4:3
            width = 400;
            height = 300;
        } else {
            // 4:3
            width = 700;
            height = 525;
        }

        const graph = new Dygraph(
            graphElement,
            formatReadingsForGraph(readings),
            {
                width: width,
                height: height,
                // make graph static/noninteractive
                interactionModel: {},  // no zooming, etc.
                drawHighlightPointCallback: () => { },  // no point highlight on hover
                showLabelsOnHighlight: false,  // no legend on hover
                // no ID column needed
                labels: ['Time', 'Temperature'],
                valueRange: [-30, 30],
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
});
