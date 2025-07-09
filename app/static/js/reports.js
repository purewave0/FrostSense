/**
 * Format the given Date as YYYY-MM-DDTHH:mm, useful for setting min/max values for
 * <datetime-local> elements.
 */
function formatDateForLocalDatetime(date) {
    // [YYYY-MM-DDTHH:mm]:ss.fffZ
    return date.toISOString().slice(0, 16);
}

/**
 * Return the given `date` (implicitly in UTC) adjusted to the local timezone.
 *
 * So a date of 00:00 UTC would be returned as 00:00 but in the local timezone.
 */
function adjustToLocalTimezone(date) {
    const timezoneOffsetMillis = date.getTimezoneOffset() * 60 * 1000;
    return new Date(date.getTime() - timezoneOffsetMillis)
}

/**
 * Return today @ 00h:01m, 1 minute later than the start of today (00h:00m).
 */
function getDateAfterStartOfToday() {
    const date = new Date();
    date.setHours(0, 1, 0);  // today @ 00h:01m:00s
    return date;
}

/**
 * Return today @ 23h:58m, 1 minute earlier than the end of today (23h:58m).
 */
function getDateBeforeEndOfToday() {
    const date = new Date();
    date.setHours(23, 58, 0);  // today @ 23h:58m:00s
    return date;
}


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


    /**
     * Set the custom Start local-datetime's max value to be today @ 23:58, 1 minute
     * earlier than the end of today (23:59)
     */
    function setCustomStartMaxBeforeEndOfToday() {
        // work in the user's timezone, as working in UTC would be quite confusing for
        // the user. for instance, in UTC-3 our 23:58 of today would be 20:58; our 00:01
        // of today would be 21:01 of *yesterday*
        customDatetimeInputs.start.max = formatDateForLocalDatetime(
            adjustToLocalTimezone(getDateBeforeEndOfToday())
        );
    }

    /**
     * Set the custom End local-datetime's min value to be today @ 00:01, 1 minute
     * later than the start of today (00:00)
     */
    function setCustomEndMinAfterStartOfToday() {
        customDatetimeInputs.end.min = formatDateForLocalDatetime(
            adjustToLocalTimezone(getDateAfterStartOfToday())
        );
    }

    // set any min/max values depending on the other end; and if 'custom' is checked,
    // require the relevant datetime input to be filled
    for (const radio of Object.values(datetimeRadios.start)) {
        radio.addEventListener('change', () => {
            customDatetimeInputs.start.max = '';
            const isCustom = datetimeRadios.start.custom.checked;
            if (isCustom) {
                // TODO: fix the difference in width when enabled/disabled
                customDatetimeInputs.start.disabled = false;
                customDatetimeInputs.start.required = true;

                const rangeEndsToday = datetimeRadios.end.today.checked;
                if (rangeEndsToday) {
                    // End is until the end of today (23:59), so Start must go UP TO
                    // 23:58
                    setCustomStartMaxBeforeEndOfToday();
                }
            } else {
                customDatetimeInputs.start.required = false;
                customDatetimeInputs.start.value = '';
                customDatetimeInputs.start.disabled = true;

                // only set the limit if needed
                const isCustomEnd = datetimeRadios.end.custom.checked;
                if (isCustomEnd) {
                    setCustomEndMinAfterStartOfToday();
                }
            }
        });
    }
    for (const radio of Object.values(datetimeRadios.end)) {
        radio.addEventListener('change', () => {
            customDatetimeInputs.end.min = '';
            const isCustom = datetimeRadios.end.custom.checked;
            if (isCustom) {
                customDatetimeInputs.end.disabled = false;
                customDatetimeInputs.end.required = true;

                const rangeStartsToday = datetimeRadios.start.today.checked;
                if (rangeStartsToday) {
                    // Start is since the start of today (00:00), so End must be AT
                    // LEAST 00:01.
                    setCustomEndMinAfterStartOfToday();
                }
            } else {
                customDatetimeInputs.end.required = false;
                customDatetimeInputs.end.value = '';
                customDatetimeInputs.end.disabled = true;

                // only set the limit if needed
                const isCustomStart = datetimeRadios.start.custom.checked;
                if (isCustomStart) {
                    setCustomStartMaxBeforeEndOfToday();
                }
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


    // ensure Start comes before End, or End comes after Start (whichever is filled
    // last)
    customDatetimeInputs.start.addEventListener('change', () => {
        if (customDatetimeInputs.start.validity.valid) {
            // End must come AFTER Start (at least 1 minute later)
            const minimumDatetime = customDatetimeInputs.start.valueAsDate;
            minimumDatetime.setMinutes(minimumDatetime.getMinutes() + 1)

            customDatetimeInputs.end.min =
                formatDateForLocalDatetime(minimumDatetime);
        } else {
            customDatetimeInputs.end.min = '';
        }
    });
    customDatetimeInputs.end.addEventListener('change', () => {
        if (customDatetimeInputs.end.validity.valid) {
            // Start must come BEFORE End (at least 1 minute earlier)
            const maximumDatetime = customDatetimeInputs.end.valueAsDate;
            maximumDatetime.setMinutes(maximumDatetime.getMinutes() - 1);

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
