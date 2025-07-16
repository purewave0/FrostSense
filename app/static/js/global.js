/**
 * Round `temperature` to 1 decimal place.
 */
function roundTemperature(temperature) {
    return Math.round(temperature * 10) / 10;
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
