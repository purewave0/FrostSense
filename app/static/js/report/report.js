document.addEventListener('DOMContentLoaded', () => {
    const locales = getUserLocales();
    if (hasTable) {
        // // TODO:
        // const rowsPerTable = (hasGraph)
        //     ? 40   // make some space for the graph
        //     : 60;
        const rowsPerTable = 50;
        let rowIndex = 0;
        const tables = []
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
                roundTemperature(reading.temperature);
            currentTable.append(row);
            ++rowIndex;
        }

        const tablesDestination = document.getElementById('tables-section');
        tablesDestination.append(...tables);
    }

    if (hasGraph) {
        // TODO
    }
});
