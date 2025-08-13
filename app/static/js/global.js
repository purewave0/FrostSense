// highlight current page link
const sidebarLinks = document.getElementById('sidebar-links');
if (sidebarLinks) {
    const currentPathname = document.location.pathname;
    for (const link of sidebarLinks.children) {
        if (link.pathname === currentPathname) {
            link.classList.add('selected');
            link.href = '#';  // no more need for the link; we're already in that page
            break;
        }
    }
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


/**
 * Format `temperature` as "<temperature> °C", with N decimal digits (default 1), and
 * with temperature being in a <span class="temperature"> tag.
 */
function formatTemperatureHTML(temperature, decimalDigits = 1) {
    return `<span class="temperature">${temperature.toFixed(decimalDigits)}</span> °C`;
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


/** Interval (in milliseconds) at which gauges and graphs will fetch updates. */
const UPDATE_INTERVAL = 2_000;  // TODO: proper value. 2s is just for testing

const ReadingsReport = {
    /** How many rows one table has. Any more, and the next readings go into a new
     *  table. */
    ROWS_PER_TABLE: 80,

}
