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

    // when 'custom' is marked, require the relevant datetime input to be filled
    for (const radio of Object.values(datetimeRadios.start)) {
        radio.addEventListener('change', () => {
            customDatetimeInputs.start.required = datetimeRadios.start.custom.checked;
        });
    }
    for (const radio of Object.values(datetimeRadios.end)) {
        radio.addEventListener('change', () => {
            customDatetimeInputs.end.required = datetimeRadios.end.custom.checked;
        });
    }

    const notes = document.getElementById('notes');
    const notesLengthCount = document.getElementById('notes-current-length');
    notes.addEventListener('input', () => {
        notesLengthCount.textContent = notes.value.trim().length;
    });
});
