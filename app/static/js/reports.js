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
            }
        });
    }

    const notes = document.getElementById('notes');
    const notesLengthCount = document.getElementById('notes-current-length');
    notes.addEventListener('input', () => {
        notesLengthCount.textContent = notes.value.trim().length;
    });
});
