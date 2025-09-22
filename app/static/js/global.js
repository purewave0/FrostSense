// highlight current page link
const sidebarLinks = document.querySelectorAll('.link-section a');
if (sidebarLinks) {
    const currentPathname = document.location.pathname;
    for (const link of sidebarLinks) {
        if (link.pathname === currentPathname) {
            link.classList.add('selected');
            link.href = '#';  // no more need for the link; we're already in that page
            break;
        }
    }
}

// header user profile
const headerAvatar = document.getElementById('header-avatar');
if (headerAvatar) {
    const profileDropdown = document.getElementById('profile-dropdown');

    function dropdownOutsideClickHandler(event) {
        if (!profileDropdown.contains(event.target)) {
            headerAvatar.dispatchEvent(new Event('click'));
        }
    }

    function dropdownEscHandler(event) {
        if (event.key === 'Escape') {
            headerAvatar.dispatchEvent(new Event('click'));
        }
    }

    headerAvatar.addEventListener('click', (event) => {
        const isShowing = profileDropdown.classList.contains('show');
        if (isShowing) {
            profileDropdown.classList.remove('show');
            document.body.removeEventListener('click', dropdownOutsideClickHandler);
            document.body.removeEventListener('keydown', dropdownEscHandler);
        } else {
            profileDropdown.classList.add('show');
            document.body.addEventListener('click', dropdownOutsideClickHandler);
            document.body.addEventListener('keydown', dropdownEscHandler);
        }
        // prevent this click from insta-closing the dropdown
        event.stopPropagation();
    });

    const dropdownMiniName = document.getElementById('mini-name');
    const dropdownMiniUsername = document.getElementById('mini-username');

    // in case they get ellipsized
    for (const element of [dropdownMiniName, dropdownMiniUsername]) {
        element.title = element.textContent.trim();
    }
}


/**
 * Return the given string with all consecutive whitespaces collapsed into one.
 */
function collapseAllWhitespace(string) {
    return string.replace(/\s+/g, ' ');
}

/**
 * Round `temperature` to 1 decimal place.
 */
function roundTemperature(temperature) {
    return Math.round(temperature * 10) / 10;
}


/**
 * Format `temperature` as "<temperature> °C", with N decimal digits (default 1)
 */
function formatTemperature(temperature, decimalDigits = 1) {
    return `${temperature.toFixed(decimalDigits)} °C`;
}

const TemperatureUnits = {
    CELSIUS: 'celsius',
    FAHRENHEIT: 'fahrenheit'
};

const TemperatureUnitStrings = {
    [TemperatureUnits.CELSIUS]: '°C',
    [TemperatureUnits.FAHRENHEIT]: '°F',
};

/**
 * Return the given Celsius value converted to Fahrenheit.
 */
function celsiusToFahrenheit(celsius) {
    return (celsius * 1.8) + 32;
}

/**
 * Return the given Celsius value converted (if necessary) to the given unit.
 * This is a convenience function, so that you don't have to do conversions yourself
 * whenever you need to provide or display a temperature value.
 *
 * @param {number} celsius The original temperature in Celsius.
 * @param {string} unit The unit to use, according to `TemperatureUnits`.
 *
 * @returns {number} The converted value.
 */
function temperatureValue(celsius, unit) {
    switch (unit) {
        case TemperatureUnits.CELSIUS:
            return roundTemperature(celsius);
        case TemperatureUnits.FAHRENHEIT:
            return roundTemperature(celsiusToFahrenheit(celsius));
    }
}


/**
 * Return the given Celsius value converted (if necessary) to the given unit and
 * formatted accordingly.
 *
 * @param {number} celsius The original temperature in Celsius.
 * @param {string} unit The unit to use, according to `TemperatureUnits`.
 * @param {number} decimalDigits The number of decimal digits (default 1).
 *
 * @returns {string} The formatted value.
 */
function formattedTemperature(celsius, unit, decimalDigits = 1) {
    switch (unit) {
        case TemperatureUnits.CELSIUS:
            return `${celsius.toFixed(decimalDigits)} °C`;
        case TemperatureUnits.FAHRENHEIT:
            return `${celsiusToFahrenheit(celsius).toFixed(decimalDigits)} °F`;
    }
}

/**
 * Format the given temperature as "`temperature` `unit string`", with `temperature`
 * being in a <span class="temperature"> tag.
 *
 * @param {number} celsius The original temperature, in Celsius, to format.
 * @param {string} unit The unit, according to `TemperatureUnits`.
 * @param {number} decimalDigits The number of decimal digits (default 1).
 */
function formattedTemperatureHTML(celsius, unit, decimalDigits = 1) {
    return `
        <span class="temperature">
            ${temperatureValue(celsius, unit).toFixed(decimalDigits)}
        </span> ${TemperatureUnitStrings[unit]}
    `;
}


/**
 * Format the given Date as YYYY-MM-DDTHH:mm, useful for setting min/max values for
 * datetime-local input elements.
 */
function formatDateForDatetimeInput(date) {
    // [YYYY-MM-DDTHH:mm]:ss.sssZ
    return date.toISOString().slice(0, 16);
}


/**
 * Format the given Date as YYYY-MM-DD, useful for setting min/max values for date input
 * elements.
 */
function formatDateForDateInput(date) {
    // [YYYY-MM-DD]THH:mm:ss.sssZ
    return date.toISOString().slice(0, 10);
}


/**
 * Format the given Date with year, month, day, hours, and minutes, all of them
 * 2-digits long, according to the user's locales.
 */
function formatDateToCompactDatetime(date, locales) {
    return date.toLocaleString(
        locales,
        {
            'year': '2-digit',
            'month': '2-digit',
            'day': '2-digit',

            'hour': '2-digit',
            'minute': '2-digit',
        }
    );
}


/**
 * Format the given Date with year, month, and day, all of them 2-digits long, according
 * to the user's locales.
 */
function formatDateToCompactDate(date, locales) {
    return date.toLocaleString(
        locales,
        {
            'year': '2-digit',
            'month': '2-digit',
            'day': '2-digit',
        }
    );
}


/**
 * Format the given Date with hours, and minute, all of them 2-digits long, according to
 * the user's locales.
 */
function formatDateToCompactTime(date, locales) {
    return date.toLocaleString(
        locales,
        {
            'hour': '2-digit',
            'minute': '2-digit',
        }
    );
}


/**
 * Return a list of the user's preferred languages.
 */
function getUserLocales() {
    return navigator.languages;
}


/**
 * Return the given `date` (implicitly in UTC) adjusted to the local timezone.
 *
 * So a date of 00:00 UTC, for example, would be returned as 00:00 but in the local
 * timezone.
 *
 * This is the reverse of adjustToUTC.
 */
function adjustToLocalTimezone(date) {
    const timezoneOffsetMillis = date.getTimezoneOffset() * 60 * 1000;
    return new Date(date.getTime() - timezoneOffsetMillis)
}

/**
 * Return the given `date` (in local time) adjusted to UTC.
 *
 * So a date of 00:00 UTC-3, for example, would be returned as 00:00 but in UTC.
 *
 * This is the reverse of adjustToLocalTimezone.
 */
function adjustToUTC(date) {
    const timezoneOffsetMillis = date.getTimezoneOffset() * 60 * 1000;
    return new Date(date.getTime() + timezoneOffsetMillis)
}

/**
 * Return today @ 00h:00m:00s.000ms.
 */
function getStartOfToday() {
    const date = new Date();
    date.setHours(0, 0, 0, 0);  // today @ 00h:00m:00s.000ms
    return date;
}

const ToastType = {
    'SUCCESS': {
        'backgroundColor': 'var(--color-toast-success)',
        'icon': `
            <svg
                xmlns="http://www.w3.org/2000/svg"
                height="24px"
                viewBox="0 -960 960 960"
                width="24px"
                fill="#e3e3e3"
            >
                <path d="M382-240 154-468l57-57 171 171 367-367 57 57-424 424Z"/>
            </svg>
        `,
    },
    'ERROR': {
        'backgroundColor': 'var(--color-toast-error)',
        'icon': `
            <svg
                xmlns="http://www.w3.org/2000/svg"
                height="24px"
                viewBox="0 -960 960 960"
                width="24px"
                fill="#e3e3e3"
            >
                <path d="M440-280h80v-240h-80v240Zm40-320q17 0 28.5-11.5T520-640q0-17-11.5-28.5T480-680q-17 0-28.5 11.5T440-640q0 17 11.5 28.5T480-600Zm0 520q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Z"/>
            </svg>
        `,
    },
};


/**
 * Show a toast of the given type with the given text for 3 seconds.
 *
 * @param {object} type The toast type, according to `ToastType`.
 * @param {string} text The toast's contents.
 */
function showToast(type, text) {
    Toastify({
        text: text,
        duration: (type === ToastType.ERROR) ? 5_000 : 3_000,
        close: true,
        stopOnFocus: false,
        gravity: 'bottom',
        position: 'right',
        style: {
            background: type.backgroundColor,
        },
    }).showToast();
}


/** Interval (in milliseconds) at which gauges and graphs will fetch updates. */
const UPDATE_INTERVAL = 2_000;  // TODO: proper value. 2s is just for testing

const ReadingsReport = {
    /** How many rows one table has. Any more, and the next readings go into a new
     *  table. */
    ROWS_PER_TABLE: 80,
}
