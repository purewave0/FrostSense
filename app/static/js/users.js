const allPermissions = [
    {
        value: 1,
        name: 'Manage reports',
    },
    {
        value: 2,
        name: 'Edit sensors',
    },
    {
        value: 4,
        name: 'Manage users',
    },
    {
        value: 8,
        name: 'Manage system settings',
    },
];

/**
 * Return true if `permissionsValue` includes `permission`.
 *
 * @param {number} permissionsValue The current permissions.
 * @param {number} permission The permission to check for.
 */
function containsPermission(permissionsValue, permission) {
    return (permissionsValue & permission) !== 0;
}


/**
 * Return an array of each permission included in the given permissions value.
 *
 * @param {number} permissionsValue The current permissions.
 */
function extractPermissionsFromNumber(permissionsValue) {
    return allPermissions.filter((permission) => {
        return containsPermission(permissionsValue, permission.value)
    });
}


/**
 * Return a string with every given permission's name, one per line.
 *
 * Each line starts with a hyphen (-). If there are no permissions at all,
 * "No permissions" is returned.
 *
 * @param {number} permissionsValue The current permissions.
 */
function formatPermissionsValue(permissionsValue) {
    if (permissionsValue === 0) {
        return 'No permissions.'
    }
    return '- ' + extractPermissionsFromNumber(permissionsValue)
        .map((permission) => permission.name)
        .join('\n- ');
}

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
                type: 'string',  /* don't treat it as a number */
                width: '160px',
                render: (data, type) => {
                    if (type === 'display') {
                        return '<span class="permissions-cell">…</span>';
                    }
                    return data;
                },
                createdCell: (cell, data) => {
                    cell.title = formatPermissionsValue(data);
                }
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
                'permissions': user.permissions,
                'updated_on': user.updated_on,
                'created_on': user.created_on,
            }
        );
    }
    table.draw();

    // TODO: constantly check for updates
});
