document.addEventListener('DOMContentLoaded', () => {
    const sensorsSelect = document.getElementById('sensor');
    // TODO: loading
    Api.fetchSensors()
        .then((response) => response.json())
        .then((sensors) => {
            for (const sensor of sensors) {
                const option = document.createElement('option');
                option.value = sensor.id;
                option.textContent = sensor.name;
                sensorsSelect.append(option);
            }
            sensorsSelect.disabled = false;
        });

    const formatSelect = document.getElementById('format');

    const datetimeRadios = {
        'start': {
            'today': document.getElementById('start-today'),
            'custom': document.getElementById('start-custom'),
        },
        'end': {
            'today': document.getElementById('end-today'),
            'custom': document.getElementById('end-custom'),
        },
    };
    const customDatetimeInputs = {
        'start': document.getElementById('start-custom-value'),
        'end': document.getElementById('end-custom-value'),
    }

    // when 'custom' is checked, require the relevant datetime input to be filled
    for (const radio of Object.values(datetimeRadios.start)) {
        radio.addEventListener('change', () => {
            const isCustom = datetimeRadios.start.custom.checked;
            if (isCustom) {
                // TODO: fix the difference in width when enabled/disabled
                customDatetimeInputs.start.disabled = false;
                customDatetimeInputs.start.required = true;
                customDatetimeInputs.start.max = '';
            } else {
                customDatetimeInputs.start.required = false;
                customDatetimeInputs.start.value = '';
                customDatetimeInputs.start.disabled = true;
            }
        });
    }
    for (const radio of Object.values(datetimeRadios.end)) {
        radio.addEventListener('change', () => {
            const isCustom = datetimeRadios.end.custom.checked;
            if (isCustom) {
                customDatetimeInputs.end.disabled = false;
                customDatetimeInputs.end.required = true;
            } else {
                customDatetimeInputs.end.required = false;
                customDatetimeInputs.end.value = '';
                customDatetimeInputs.end.disabled = true;
                customDatetimeInputs.end.min = '';
            }
        });
    }

    const notes = document.getElementById('notes');
    const notesLengthCount = document.getElementById('notes-current-length');
    notes.addEventListener('input', () => {
        notesLengthCount.textContent = notes.value.trim().length;
    });


    // -- validation --

    /**
     * Return the start of the time range. Depends on what type of Start is checked.
     *
     * @returns {string} "today" if "Start of today" is checked.
     * @returns {?Date} when "Custom" is checked: the custom datetime if it has been
     *     filled, otherwise null.
     */
    function getRangeStart() {
        if (datetimeRadios.start.today.checked) {
            return 'today';
        }

        if (!customDatetimeInputs.start.validity.valid) {
            return null;
        }

        return customDatetimeInputs.start.valueAsDate;
    }

    /**
     * Return the end of the time range. Depends on what type of End is checked.
     *
     * @returns {string} "today" if "End of today" is checked.
     * @returns {?Date} when "Custom" is checked: the custom datetime if it has been
     *     filled, otherwise null.
     */
    function getRangeEnd() {
        if (datetimeRadios.end.today.checked) {
            return 'today';
        }

        if (!customDatetimeInputs.end.validity.valid) {
            return null;
        }

        return customDatetimeInputs.end.valueAsDate;
    }

    /**
     * Format the given Date as YYYY-MM-DDTHH:mm, useful for setting min/max values for
     * <datetime-local> elements.
     */
    function formatDateForLocalDatetime(date) {
        // [YYYY-MM-DDTHH:mm]:ss.fffZ
        return date.toISOString().slice(0, 16);
    }

    // TODO: handle the case when either Start or End is "today"

    // ensure Start comes before End, or End comes after Start (whichever is filled
    // last)
    customDatetimeInputs.start.addEventListener('change', () => {
        if (customDatetimeInputs.start.validity.valid) {
            // End must come AFTER Start (at least 1 minute later)
            const startDatetime = customDatetimeInputs.start.valueAsDate;
            const minimumDatetime = new Date(
                startDatetime.setMinutes(startDatetime.getMinutes() + 1)
            );
            customDatetimeInputs.end.min =
                formatDateForLocalDatetime(minimumDatetime);
        } else {
            customDatetimeInputs.end.min = '';
        }
    });
    customDatetimeInputs.end.addEventListener('change', () => {
        if (customDatetimeInputs.end.validity.valid) {
            // Start must come BEFORE End (at least 1 minute earlier)
            const endDatetime = customDatetimeInputs.end.valueAsDate;
            const maximumDatetime = new Date(
                endDatetime.setMinutes(
                    endDatetime.getMinutes() - 1
                )
            );
            customDatetimeInputs.start.max =
                formatDateForLocalDatetime(maximumDatetime);
        } else {
            customDatetimeInputs.start.max = '';
        }
    });

    const form = document.getElementById('report-form');
    form.addEventListener('submit', (event) => {
        // TODO: cancel submission when the total of readings is 0

        alert(
            `sensor_id=${Number(sensorsSelect.value)}`
            + `\nformat=${formatSelect.value}`
            + `\nstart=${getRangeStart()}`
            + `\nend=${getRangeEnd()}`
            + `\nnotes=${notes.value.trim() || '(no notes)'}`
        );

        event.preventDefault();
    });
});
