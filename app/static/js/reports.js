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

    const notes = document.getElementById('notes');
    const notesLengthCount = document.getElementById('notes-current-length');
    notes.addEventListener('input', () => {
        notesLengthCount.textContent = notes.value.trim().length;
    });
});
