document.addEventListener('DOMContentLoaded', () => {
    const codeInput = document.getElementById('code');
    const codeForm = document.getElementById('code-form');
    const fetchReportButton = document.getElementById('fetch');

    const mask = IMask(codeInput, {
        mask: '####\\—####\\—##',
        prepareChar: str => str.toUpperCase(),
        definitions: {
            '#': /[0-9A-Z]/,
        },
        lazy: false, // always show placeholder
        placeholderChar: '_',
    });

    codeForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const codeValue = mask.unmaskedValue.toLowerCase();

        const url = `/reports/${codeValue}`;
        // TODO: loading
        const response = await fetch(url);
        if (!response.ok) {
            showToast(
                ToastType.ERROR, 'Report not found'
            );
            return;
        }

        showToast(
            ToastType.SUCCESS, 'Report fetched successfully'
        );
        fetchReportButton.disabled = true;
        setTimeout(() => {
            window.open(`/reports/${codeValue}`, '_blank').focus();
            fetchReportButton.disabled = false;
        }, 700);
    });
});
