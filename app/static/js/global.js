/**
 * Round `temperature` to 1 decimal place.
 */
function roundTemperature(temperature) {
    return Math.round(temperature * 10) / 10;
}


/** Interval (in milliseconds) at which gauges and graphs will fetch updates. */
const UPDATE_INTERVAL = 2_000;  // TODO: proper value. 2s is just for testing
