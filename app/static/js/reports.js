document.addEventListener('DOMContentLoaded', () => {
    const notes = document.getElementById('notes');
    const notesLengthCount = document.getElementById('notes-current-length');
    notes.addEventListener('input', () => {
        notesLengthCount.textContent = notes.value.trim().length;
    });
});
