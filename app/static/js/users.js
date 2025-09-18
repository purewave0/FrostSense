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
function hasPermission(permissionsValue, permission) {
    return (permissionsValue & permission) !== 0;
}


/**
 * Return an array of each permission included in the given permissions value.
 *
 * @param {number} permissionsValue The current permissions.
 */
function extractPermissionsFromNumber(permissionsValue) {
    return allPermissions.filter((permission) => {
        return hasPermission(permissionsValue, permission.value)
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


/**
 * Colour the given row blue, then return it to its original colour after
 * `millisDuration` milliseconds.
 */
function animateRowUpdate(rowElement, millisDuration) {
    rowElement.classList.add('recently-updated');
    setTimeout(() => {
        rowElement.classList.remove('recently-updated');
    }, millisDuration);
}


document.addEventListener('DOMContentLoaded', async () => {
    const UPDATED_ROW_COLOUR_DURATION = 1_500;
    const DATETIME_COLUMN_WIDTH = '190px';
    const locales = getUserLocales();

    let selectedUser = null;

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
                render: (_, __, user) => {
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
                    editButton.addEventListener('click', () => {
                        selectedUser = user;
                        openEditModal(user.display_name, user.permissions);
                    });

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
                    resetPasswordButton.addEventListener('click', () => {
                        selectedUser = user;
                        openResetPasswordModal(user.display_name);
                    });

                    const cell = document.createElement('div');
                    cell.className = 'actions-cell';
                    cell.append(editButton, resetPasswordButton);
                    return cell;
                }
            }
        ],
        rowCallback: (row, userData) => {
            const nameCell = row.cells[0];
            nameCell.title =
                `Display name: ${userData.display_name}`
                + `\nUsername: ${userData.username}`;

            const permissionsCell = row.cells[1];
            permissionsCell.title = formatPermissionsValue(userData.permissions);
        },
        order: [
            [1, 'asc'],
        ]
    });

    let latestUpdateDate = null;
    let tableUserIds = [];
    const response = await Api.fetchUsers();
    const users = await response.json();

    for (const user of users) {
        const updatedOn = new Date(user.updated_on);
        if (latestUpdateDate === null || updatedOn > latestUpdateDate) {
            latestUpdateDate = updatedOn;
        }

        if (user.id === currentUserId) {
            // don't let users see themselves
            continue;
        }

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
        tableUserIds.push(user.id);
    }
    table.draw();

    async function fetchAndApplyTableUpdates() {
        console.log(`users.js: fetching updates after ${latestUpdateDate}`)
        const response = await Api.fetchUsers(latestUpdateDate);
        const updatedUsers = await response.json();
        const updatedRowIndices = [];

        for (const user of updatedUsers) {
            if (user.id === currentUserId) {
                // the current user is never in the table
                continue;
            }

            const updatedOn = new Date(user.updated_on);
            if (latestUpdateDate === null || updatedOn > latestUpdateDate) {
                latestUpdateDate = updatedOn;
            }

            const isNewlyCreated = !tableUserIds.includes(user.id);
            if (isNewlyCreated) {
                console.log('users.js: newly created user:', user);
                const newRowIndex = table.row.add(
                    {
                        'id': user.id,
                        'display_name': user.display_name,
                        'username': user.username,
                        'permissions': user.permissions,
                        'updated_on': user.updated_on,
                        'created_on': user.created_on,
                    }
                ).index();
                updatedRowIndices.push(newRowIndex);

                tableUserIds.push(user.id);
            } else {
                // the user already exists; reflect the changes
                console.log('users.js: edited user:', user);
                const editedRowIndex = table
                    .row((_, userData) => userData.id === user.id)
                    .data(
                        {
                            'id': user.id,
                            'display_name': user.display_name,
                            'username': user.username,
                            'permissions': user.permissions,
                            'updated_on': user.updated_on,
                            'created_on': user.created_on,
                        }
                    );
                updatedRowIndices.push(editedRowIndex);
            }
        }

        if (updatedRowIndices.length > 0) {
            console.log('users.js: updates were made. redrawing table')
            table.draw();
            for (const index of updatedRowIndices) {
                const rowElement = table.row(index).node();
                animateRowUpdate(rowElement, UPDATED_ROW_COLOUR_DURATION);
            }
        }
    }

    setInterval(fetchAndApplyTableUpdates, 5_000);


    // -- actions/modals --

    // -- Create modal --
    const createButton = document.getElementById('top-action-create');
    createButton.addEventListener('click', () => {
        openCreateModal();
    });

    /**
     * Return the given string without any whitespace characters.
     */
    function eraseAllWhitespace(string) {
        return string.replace(/\s/g, '');
    }

    const createModal = {
        'form': document.getElementById('modal-create-form'),
        'displayName': document.getElementById('modal-create-display-name'),
        'username': document.getElementById('modal-create-username'),
        'permissions': document.querySelectorAll(
            'input[type="checkbox"][name="create-permissions"]'
        ),
    };
    createModal.displayName.addEventListener('input', () => {
        createModal.displayName.value =
            collapseAllWhitespace(createModal.displayName.value);
    });
    createModal.username.addEventListener('input', () => {
        createModal.username.value = eraseAllWhitespace(createModal.username.value);
    });
    createModal.form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const displayName = createModal.displayName.value.trim();
        const username = createModal.username.value.trim();
        let permissionsValue = 0;
        for (const permissionCheckbox of createModal.permissions) {
            if (permissionCheckbox.checked) {
                permissionsValue += Number(permissionCheckbox.value);
            }
        }

        const response = await Api.createUser(
            displayName,
            username,
            permissionsValue
        );

        if (!response.ok) {
            const error = (await response.json()).error;
            switch (error) {
                case 'username_already_exists':
                    createModal.username
                        .setCustomValidity('This username already exists.');
                    createModal.username.reportValidity();
                    createModal.username.focus();
                    createModal.username.setCustomValidity('');
                    break;
                default:
                    // TODO: handle other errors
                    alert('TODO other errors');
                    break;
            }
            return;
        }

        const newUser = await response.json();
        // we'll push the id into `tableUserIds` only once the new table row is added

        MicroModal.close('modal-create');
        createModal.form.reset();

        // TODO: add new user row
        openTemporaryPasswordModal(
            newUser.display_name, newUser.username, newUser.temporary_password
        );

        await fetchAndApplyTableUpdates();
    });

    function openCreateModal() {
        createModal.form.reset();  // clear any cache
        MicroModal.show('modal-create');
    }

    // -- Temporary Password modal (for Create & Reset Password modals) --
    const temporaryPasswordModal = {
        'displayName': document.getElementById('modal-temporary-password-display-name'),
        'username': document.getElementById('modal-temporary-password-username'),
        'passwordWrapper':
            document.getElementById('modal-temporary-password-password-wrapper'),
        'password': document.getElementById('modal-temporary-password-password'),
    };
    temporaryPasswordModal.passwordWrapper.addEventListener('click', () => {
        temporaryPasswordModal.passwordWrapper.classList.add('revealed');
    });

    function openTemporaryPasswordModal(displayName, username, password) {
        temporaryPasswordModal.displayName.textContent = displayName;
        temporaryPasswordModal.username.textContent = username;
        temporaryPasswordModal.passwordWrapper.classList.remove('revealed');
        temporaryPasswordModal.password.textContent = password;
        MicroModal.show('modal-temporary-password', {
            onClose() {
                temporaryPasswordModal.password.textContent = '';
                selectedUser = null;
            },
        });
    }


    // -- Edit modal --
    const editModal = {
        'form': document.getElementById('modal-edit-form'),
        'displayName': document.getElementById('modal-edit-display-name'),
        'permissions': document.querySelectorAll(
            'input[type="checkbox"][name="edit-permissions"]'
        ),
    };
    editModal.displayName.addEventListener('input', () => {
        editModal.displayName.value =
            collapseAllWhitespace(editModal.displayName.value);
    });
    editModal.form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const displayName = editModal.displayName.value.trim();
        let permissionsValue = 0;
        for (const permissionCheckbox of editModal.permissions) {
            if (permissionCheckbox.checked) {
                permissionsValue += Number(permissionCheckbox.value);
            }
        }

        const wereChangesMade = (
            selectedUser.display_name !== displayName
            || permissionsValue !== selectedUser.permissions
        );
        if (!wereChangesMade) {
            // TODO: show proper alert
            alert('no changes made')
            MicroModal.close('modal-edit');
            return;
        }

        await Api.editUser(selectedUser.id, displayName, permissionsValue);
        // TODO: handle errors
        await fetchAndApplyTableUpdates();
        MicroModal.close('modal-edit');
        editModal.form.reset();
        selectedUser = null;
    });

    function openEditModal(displayName, permissionsValue) {
        editModal.displayName.value = displayName;
        editModal.displayName.placeholder = displayName;

        for (const permissionCheckbox of editModal.permissions) {
            const hasThisPermission = hasPermission(
                permissionsValue, permissionCheckbox.value
            );
            if (hasThisPermission) {
                permissionCheckbox
                    .parentElement  // div
                    .parentElement  // li
                    .classList.add('currently-granted');
                permissionCheckbox.checked = true;
            } else {
                permissionCheckbox
                    .parentElement
                    .parentElement
                    .classList.remove('currently-granted');
                permissionCheckbox.checked = false;
            }
        }
        MicroModal.show('modal-edit');
    }


    // -- Reset password modal --
    const resetPasswordModal = {
        'displayName': document.getElementById('modal-reset-password-display-name'),
        'confirmButton': document.getElementById('modal-reset-password-confirm'),
    };
    resetPasswordModal.confirmButton.addEventListener('click', async () => {
        const response = await Api.resetUserPassword(selectedUser.id);
        // TODO: handle errors
        await fetchAndApplyTableUpdates();  // just update the `updated_on` date
        const temporaryPassword = await response.json();

        MicroModal.close('modal-reset-password');
        openTemporaryPasswordModal(
            selectedUser.display_name, selectedUser.username, temporaryPassword
        );
    });

    function openResetPasswordModal(displayName) {
        resetPasswordModal.displayName.textContent = displayName;
        MicroModal.show('modal-reset-password');
    }
});
