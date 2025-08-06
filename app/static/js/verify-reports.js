document.addEventListener('DOMContentLoaded', () => {
    const codeInput = document.getElementById('code');
    const codeForm = document.getElementById('code-form');

    const mask = IMask(codeInput, {
        mask: '####\\—####\\—##',
        prepareChar: str => str.toUpperCase(),
        definitions: {
            '#': /[0-9A-Z]/,
        },
        lazy: false, // always show placeholder
        placeholderChar: '_',
    });

    codeForm.addEventListener('submit', (event) => {
        event.preventDefault();
        alert('TODO');
    });
});
