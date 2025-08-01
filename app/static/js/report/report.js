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
    const headerTimezone = document.getElementById('timezone-value');
    headerTimezone.textContent = Intl.DateTimeFormat().resolvedOptions().timeZone;

    new QRCode(
        document.getElementById('qr-code'),
        {
            text: token,
            width: 72,
            height: 72,
            drawer: 'svg',
        }
    );
    const locales = getUserLocales();
    if (hasTable) {
        let rowIndex = 0;
        const tables = [];
        let previousDate = null;
        // use the horizontal space by distributing readings between multiple tables.
        // this avoids creating multiple pages unnecessarily
        for (const reading of readings) {
            const shouldCreateTable = rowIndex % ReadingsReport.ROWS_PER_TABLE === 0;
            if (shouldCreateTable) {
                const table = document.createElement('table');
                table.className = 'table';
                tables.push(table);
            }

            const currentTable = tables.at(-1);

            const currentDate = new Date(reading.created_on);

            const isNewDay = (
                previousDate === null
                || previousDate.getDate() != currentDate.getDate()
            );

            if (isNewDay) {
                const isFirstDay = previousDate === null;
                if (!isFirstDay) {
                    // add an empty row to work as a spacer
                    const spacerRow = document.createElement('tr');
                    spacerRow.className = 'table-spacer';
                    currentTable.append(spacerRow);
                    // count it as a row so we don't misalign the tables
                    ++rowIndex;
                }
                const dayRow = document.createElement('tr');
                dayRow.className = 'table-day';
                dayRow.innerHTML = '<td class="day-value" colspan="2"></td>';
                dayRow.querySelector('.day-value').textContent =
                    formatDateToCompactDate(currentDate, locales);
                currentTable.append(dayRow);

                // count it as a row too
                ++rowIndex;
            }

            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="datetime"></td>
                <td class="temperature">°C</td>
            `;
            let formattedTime = formatDateToCompactTime(currentDate, locales);
            previousDate = currentDate;
            row.querySelector('.datetime').textContent = formattedTime;
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
            width = 800;
            height = 600;
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
