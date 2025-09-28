/**
 * Return the given date 23h:59m:59s.999ms later.
 */
function getEndOfDay(date) {
    date.setHours(date.getHours() + 23);
    date.setMinutes(date.getMinutes() + 59);
    date.setSeconds(date.getSeconds() + 59);
    date.setMilliseconds(date.getMilliseconds() + 999);
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
            updateReadingsCount();
        });

    const formatSelect = document.getElementById('format');

    const timeframeRadios = {
        'single': document.getElementById('single-timeframe'),
        'range': document.getElementById('range-timeframe'),
    };
    const singleDateInput = document.getElementById('single-value');
    const rangeDateInputs = {
        'start': document.getElementById('start-value'),
        'end': document.getElementById('end-value'),
    };

    // select today by default
    singleDateInput.valueAsDate = new Date();

    // if 'range' is checked, require its inputs to be filled
    for (const radio of Object.values(timeframeRadios)) {
        radio.addEventListener('change', () => {
            const isRange = timeframeRadios.range.checked;
            singleDateInput.value = '';
            singleDateInput.disabled = isRange;
            singleDateInput.required = !isRange;

            for (const point in rangeDateInputs) {
                // TODO: fix the difference in width when enabled/disabled
                const input = rangeDateInputs[point];
                input.disabled = !isRange;
                input.required = isRange;
                input.value = '';
            }
        });
    }

    const notes = document.getElementById('notes');
    const notesLengthCount = document.getElementById('notes-current-length');
    notes.addEventListener('input', () => {
        const length = notes.value.trim().length;
        notesLengthCount.textContent = length;
        // reflect Notes in the preview
        if (length) {
            reportPreview.classList.add('has-notes');
        } else {
            reportPreview.classList.remove('has-notes');
        }
    });


    // -- validation --

    /**
     * Return the start of the time range.
     *
     * @returns {?Date} The date value in UTC if valid, otherwise null.
     */
    function getRangeStart() {
        if (timeframeRadios.single.checked) {
            if (!singleDateInput.validity.valid) {
                return null;
            }
            // for user convenience, the range date inputs are in the local timezone;
            // so adjust them back to UTC.
            // besides that, no other adjustment is needed. the time is already 00:00
            return adjustToUTC(singleDateInput.valueAsDate);
        }

        if (!rangeDateInputs.start.validity.valid) {
            return null;
        }
        return adjustToUTC(rangeDateInputs.start.valueAsDate);
    }

    /**
     * Return the end of the time range.
     *
     * @returns {?Date} The date value in UTC if valid, otherwise null.
     */
    function getRangeEnd() {
        if (timeframeRadios.single.checked) {
            if (!singleDateInput.validity.valid) {
                return null;
            }
            return adjustToUTC(
                getEndOfDay(singleDateInput.valueAsDate)
            );
        }

        if (!rangeDateInputs.end.validity.valid) {
            return null;
        }

        return adjustToUTC(
            getEndOfDay(rangeDateInputs.end.valueAsDate)
        );
    }

    /**
     * Return the Notes value.
     *
     * @returns {?string} The trimmed Notes value, or null if empty or whitespace-only.
     */
    function getNotesValue() {
        return notes.value.trim() || null
    }

    // set min/max limits based on whichever point (Start/End) is filled last
    rangeDateInputs.start.addEventListener('change', () => {
        if (rangeDateInputs.start.validity.valid) {
            // End must not come before Start
            const minimumDate = rangeDateInputs.start.valueAsDate;
            rangeDateInputs.end.min =
                formatDateForDateInput(minimumDate);
        } else {
            rangeDateInputs.end.min = '';
        }
    });
    rangeDateInputs.end.addEventListener('change', () => {
        if (rangeDateInputs.end.validity.valid) {
            // Start must not come after End
            const maximumDate = rangeDateInputs.end.valueAsDate;
            rangeDateInputs.start.max =
                formatDateForDateInput(maximumDate);
        } else {
            rangeDateInputs.start.max = '';
        }
    });

    // inputs that filter the readings that will be included in the report
    const filterInputs = [
        sensorsSelect,
        timeframeRadios.single,
        timeframeRadios.range,
        singleDateInput,
        rangeDateInputs.start,
        rangeDateInputs.end,
    ];

    async function generateAndOpenReport() {
        showButtonLoader(generateReportButton);
        const response = await Api.createReport(
            Number(sensorsSelect.value),
            getRangeStart(),
            getRangeEnd(),
            formatSelect.value,
            getNotesValue()
        );
        if (!response.ok) {
            const error = (await response.json()).error;
            showToast(
                ToastType.ERROR, `Failed to generate report (${error})`
            );
            hideButtonLoader(generateReportButton);
            return;
        }

        const reportCode = await response.json();
        showToast(ToastType.SUCCESS, 'Report generated successfully');
        setTimeout(() => {
            window.open(`/reports/${reportCode}?should_print=1`, '_blank').focus();
            hideButtonLoader(generateReportButton);
        }, 700);
    }

    const emptyReportModal = {
        'confirmButton': document.getElementById('modal-empty-report-confirm'),
    };
    emptyReportModal.confirmButton.addEventListener('click', async () => {
        generateAndOpenReport();
        MicroModal.close('modal-empty-report');
    });
    function openEmptyReportModal() {
        MicroModal.show('modal-empty-report');
    }

    const readingsCountElement = document.getElementById('readings-count');

    function updateReadingsCount() {
        if (!form.checkValidity()) {
            readingsCountElement.textContent = '…';
            return;
        }

        // TODO: loading
        generateReportButton.disabled = true;
        readingsCountElement.classList.add('loading');

        readingsCount = Api.fetchSensorReadingsInTimeRange(
            Number(sensorsSelect.value),
            getRangeStart().toISOString(),
            getRangeEnd().toISOString(),
        ).then(
            response => response.json()
        ).then(count => {
            readingsCount = count;
            readingsCountElement.textContent = count;
            readingsCountElement.classList.remove('loading');
        }).finally(() => {
            generateReportButton.disabled = false;
        });
    }

    let readingsCount = null;
    for (const filterInput of filterInputs) {
        filterInput.addEventListener('change', updateReadingsCount);
    }

    const form = document.getElementById('report-form');
    const generateReportButton = document.getElementById('generate');
    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        if (!readingsCount) {
            // confirm with the user if they really want to generate an empty report
            openEmptyReportModal();
            return;
        }

        generateAndOpenReport();
    });

    const reportPreview = document.getElementById('preview');
    // reflect data format changes in the preview
    formatSelect.addEventListener('change', () => {
        reportPreview.dataset.format = formatSelect.value;
    });
    reportPreview.dataset.format = formatSelect.value;
});
