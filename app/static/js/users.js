
document.addEventListener('DOMContentLoaded', async () => {
    const locales = getUserLocales();
    const table = new DataTable('#users-table', {
        columns: [
            {
                name: 'id',
                data: 'id',
                orderable: false,
                visible: false,
                searchable: false,
            },
            {
                name: 'display_name',
                data: 'display_name',
            },
            {
                name: 'username',
                data: 'username',
                visible: false,
                searchable: false,
            },
            {
                name: 'permissions',
                data: 'permissions',
                searchable: false,
                orderable: false,
            },
            {
                name: 'updated_on',
                data: 'updated_on',
                render: (data, type) => {
                    if (type === 'display') {
                        return formatDateToCompactDatetime(new Date(data), locales);
                    }
                    return data;
                },
            },
            {
                name: 'created_on',
                data: 'created_on',
                render: (data, type) => {
                    if (type === 'display') {
                        return formatDateToCompactDatetime(new Date(data), locales);
                    }
                    return data;
                },
            },
        ],
        order: [
            [1, 'asc'],
        ]
    });

    const response = await Api.fetchUsers();
    const users = await response.json();

    for (const user of users) {
        table.row.add(
            {
                'id': user.id,
                'display_name': user.display_name,
                'username': user.username,
                'permissions': 'TODO', // TODO
                'updated_on': user.updated_on,
                'created_on': user.created_on,
            }
        );
    }
    table.draw();

    // TODO: constantly check for updates
});
