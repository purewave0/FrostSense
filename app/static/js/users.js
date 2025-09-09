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
    const DATETIME_COLUMN_WIDTH = '190px';
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
                width: DATETIME_COLUMN_WIDTH,
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
                width: DATETIME_COLUMN_WIDTH,
                render: (data, type) => {
                    if (type === 'display') {
                        return formatDateToCompactDatetime(new Date(data), locales);
                    }
                    return data;
                },
            },
            {
                name: 'actions',
                data: null,
                width: '100px',
                searchable: false,
                orderable: false,
                render: (data) => {
                    const editButton = document.createElement('button');
                    editButton.className = 'action action-edit';
                    editButton.title = 'Edit';
                    editButton.innerHTML = `
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            height="24px"
                            viewBox="0 -960 960 960"
                            width="24px"
                            fill="#e3e3e3"
                        >
                            <path d="M120-120v-170l528-527q12-11 26.5-17t30.5-6q16 0 31 6t26 18l55 56q12 11 17.5 26t5.5 30q0 16-5.5 30.5T817-647L290-120H120Zm584-528 56-56-56-56-56 56 56 56Z"/>
                        </svg>
                    `;

                    const resetPasswordButton = document.createElement('button');
                    resetPasswordButton.className = 'action action-reset-password';
                    resetPasswordButton.title = 'Reset password';
                    resetPasswordButton.innerHTML = `
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            height="24px"
                            viewBox="0 -960 960 960"
                            width="24px"
                            fill="#e3e3e3"
                        >
                            <path d="M480-80q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480h80q0 66 25 124.5t68.5 102q43.5 43.5 102 69T480-159q134 0 227-93t93-227q0-134-93-227t-227-93q-89 0-161.5 43.5T204-640h116v80H80v-240h80v80q55-73 138-116.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Zm-80-240q-17 0-28.5-11.5T360-360v-120q0-17 11.5-28.5T400-520v-40q0-33 23.5-56.5T480-640q33 0 56.5 23.5T560-560v40q17 0 28.5 11.5T600-480v120q0 17-11.5 28.5T560-320H400Zm40-200h80v-40q0-17-11.5-28.5T480-600q-17 0-28.5 11.5T440-560v40Z"/>
                        </svg>
                    `;

                    const cell = document.createElement('div');
                    cell.className = 'actions-cell';
                    cell.append(editButton, resetPasswordButton);
                    return cell;
                }
            }
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
