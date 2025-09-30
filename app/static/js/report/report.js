function formatAndConvertReadingsForGraph(rawReadings, temperatureUnit) {
    // the format dygraphs expects is:
    // [
    //     [x,y], [x,y], [x,y]...
    // ] for data x and y.
    return rawReadings.map((reading) => {
        return [
            new Date(reading.created_on),
            temperatureValue(reading.temperature, temperatureUnit),
        ]
    });
}

document.addEventListener('DOMContentLoaded', () => {
    function printReportIfNeeded() {
        const urlParams = new URLSearchParams(window.location.search);
        // we don't want to auto-print the report if the user came from, e.g. the Verify
        // Reports page
        const cameFromGenerateReportsPage = urlParams.get('should_print');
        if (cameFromGenerateReportsPage) {
            // we need to wait a little bit, or else the page behind the Print dialog
            // will be missing
            setTimeout(print, 50);
        }
    }

    const headerTimezone = document.getElementById('timezone-value');
    headerTimezone.textContent = Intl.DateTimeFormat().resolvedOptions().timeZone;

    const printButton = document.getElementById('print-button');
    printButton.addEventListener('click', () => {
        print();
    });

    // datetimes that will be adjusted and formatted
    const datetimes = document.querySelectorAll('.datetime');
    for (const datetime of Array.from(datetimes)) {
        const adjusted = adjustToLocalTimezone(
            new Date(datetime.textContent)
        );
        datetime.textContent = formatDateToCompactDatetime(adjusted);
    }

    new QRCode(
        document.getElementById('qr-code'),
        {
            text: code,
            width: 72,
            height: 72,
            drawer: 'svg',
        }
    );

    if (readings.length === 0) {
        printReportIfNeeded();
        return;
    }

    const locales = getUserLocales();
    if (hasTable) {
        let rowIndex = 0;
        const tables = [];
        let previousDate = null;
        let rowsPerTable = (hasNotes)
            ? ReadingsReport.rowsPerTable.withNotes
            : ReadingsReport.rowsPerTable.withoutNotes;

        // use the horizontal space by distributing readings between multiple tables.
        // this avoids creating multiple pages unnecessarily
        for (const reading of readings) {
            const shouldCreateTable = rowIndex % rowsPerTable === 0;
            if (shouldCreateTable) {
                const table = document.createElement('div');
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
                    const spacerRow = document.createElement('div');
                    spacerRow.className = 'table-row spacer';
                    currentTable.append(spacerRow);
                    // count it as a row so we don't misalign the tables
                    ++rowIndex;
                }
                const dayRow = document.createElement('div');
                dayRow.className = 'table-row';
                dayRow.innerHTML = '<div class="table-cell day"></div>';
                dayRow.querySelector('.table-cell.day').textContent =
                    formatDateToCompactDate(
                        currentDate, // no adjustment needed
                        locales
                    );
                currentTable.append(dayRow);

                // count it as a row too
                ++rowIndex;
            }

            const row = document.createElement('div');
            row.className = 'table-row';
            row.innerHTML = `
                <div class="table-cell datetime"></div>
                <div class="table-cell temperature"></div>
            `;
            let formattedTime = formatDateToCompactTime(currentDate, locales);
            previousDate = currentDate;
            row.querySelector('.datetime').textContent = formattedTime;
            row.querySelector('.temperature').textContent = (
                (reading.temperature !== null)
                    ? temperatureValue(reading.temperature, temperatureUnit).toFixed(1)
                    : 'N/A'
            );

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
        let graphLineWidth = null;
        if (hasTable) {
            // 4:3
            width = 400;
            height = 300;
            graphLineWidth = 1.5;
        } else {
            // 4:3
            width = 800;
            height = 600;
            graphLineWidth = 2;
        }

        const bodyStyle = window.getComputedStyle(document.body);
        const graphLineColour = bodyStyle.getPropertyValue('--color-graph-line');

        const minimumGraphValue = temperatureValue(minimumGraphValueRaw, temperatureUnit);
        const maximumGraphValue = temperatureValue(maximumGraphValueRaw, temperatureUnit);
        const unitString = TemperatureUnitString[temperatureUnit];

        const graph = new Dygraph(
            graphElement,
            formatAndConvertReadingsForGraph(readings, temperatureUnit),
            {
                width: width,
                height: height,
                color: graphLineColour,
                strokeWidth: graphLineWidth,
                // make graph static/noninteractive
                interactionModel: {},  // no zooming, etc.
                drawHighlightPointCallback: () => { },  // no point highlight on hover
                showLabelsOnHighlight: false,  // no legend on hover
                // no ID column needed
                labels: ['Time', 'Temperature'],
                valueRange: [minimumGraphValue, maximumGraphValue],
                axes: {
                    y: {
                        axisLabelFormatter(temperature) {
                            // temperature already in the proper unit
                            return `${temperature} ${unitString}`;
                        },
                    },
                }
            }
        );
    }

    printReportIfNeeded();
});
