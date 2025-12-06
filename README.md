:uk: **English** | [:brazil: Português](README.pt-br.md)

# FrostSense

Real-time IoT temperature monitoring solution for cold storage warehouses.

![FrostSense screenshot, Readings page](screenshots/readings.png)
![FrostSense screenshot, History page](screenshots/history.png)
![FrostSense screenshot, Reports page](screenshots/reports.png)

- Live multi-sensor temperature readings
- Customisable reports (sensor, data format, time frame, notes)
- Verify reports by their unique code
- Celsius & Fahrenheit support
- User management with permissions system
- User preferences
- System settings
- API with sensor key authentication
- Fully responsive interface
- CLI for technical tasks


## Installation

Ensure MariaDB is installed and running before starting.
[See the installation guide](https://mariadb.com/get-started-with-mariadb/).

1. Clone the repository:
    ```sh
    git clone https://github.com/purewave0/FrostSense.git
    cd FrostSense
    ```

2. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

3. Create a `.env` file in the project root with the following sample configuration:

    ```properties
    DATABASE_URL=mariadb://USERNAME:PASSWORD@localhost:3306/DATABASE_NAME
    SECRET_KEY=YOUR_SECRET_KEY
    DEBUG=False
    ```

    Replace values as needed.


## Usage

To run Frostsense, execute:
```sh
flask run
```

An admin account will be automatically created; temporary credentials will be printed
to the terminal and saved to `ADMIN-ACCOUNT.txt` at the project root.

Access the web interface at `http://localhost:5000` and log into the admin account.
You'll be prompted to create a password.

### Sensors & Readings

Once logged in, head over to the **Sensors** page; you'll see it's empty. Let's create
a few sensors:
```sh
flask seed sensors  # optional: --count=N to add N sensors (default 4)
```

You (and any users with edit permissions) can rename a sensor by hovering over it and
clicking the Edit icon.

Now, head over to either **Readings** (latest data) or **History** (data by day).
The sensors are empty, so let's seed some sample readings.
```sh
flask seed readings --continuous
```

This sends readings every 2 seconds (customise with `--interval=N`). If you want to
send many readings at once instead, run:
```sh
flask seed readings
```

You'll instantly see the new data coming in.

### User Management

User management is limited to the admin and done on the **Users** page.

At first the table will be empty; let's add some users.

While you can do so through the **Create** button, try seeding them through the CLI:
```sh
flask seed users  # optional: --count=N (default 4)
```

Hover over a user's row to see actions (edit, reset password, delete).

Hover over the Permissions cell in a user's row to see their permissions.

#### Recovery

If the admin password is ever lost or leaked, reset it with:
```sh
flask admin reset-password
# > ...
# > new temporary password: xxxxxxxxxxxx
```

Once signed in, you'll be prompted to create a new password.

### Preparing sensor devices

Sensor management is meant for technicians and limited to the CLI.

Each sensor has a unique key used by the API to authenticate incoming readings. This
prevents fake readings from unknown devices.

A **device** can be anything that can connect to a temperature sensor and send HTTP
requests: ESP32 boards, Raspberry Pis, etc.

When preparing a new device, first create a new sensor:
```sh
flask sensors create SENSOR_NAME
# > created sensor with id=SENSOR_ID
```

Use the ID printed by the command (or look for it with `flask sensors list`) to get the
newly-created sensor's key:
```sh
flask sensors show SENSOR_ID
# > ...
# > key: xxxxxxxxxxxxxxxxxxxxxxxx
```

Store the key on the board/device to include it with every request (see the next
section).

If a sensor key is ever leaked, you can reset it by running:
```sh
flask sensors reset-key SENSOR_ID
# > ...
# > new key: xxxxxxxxxxxxxxxxxxxxxxxx
```

The device with the old key will no longer be able to send readings.

To delete a sensor, get its ID with `flask sensors list` and simply run:
```sh
flask sensors delete SENSOR_ID
```

### Sending readings

To send a reading, the device should send a POST request to `/api/sensors/<SENSOR_ID>`
with the `Authorization` header set to the sensor key, and the following JSON body:
```js
{
    "temperature": TEMPERATURE,  // in Celsius
}
```

Temperatures should be sent in Celsius.

On success, HTTP 204 is returned.


## Testing

First, install the dependencies:
```sh
pip3 install -r requirements-dev.txt
```

Run all tests with:
```sh
python3 -m pytest
```

## TODO

- Webhook integration for alerts
- API documentation with Swagger
- Frontend internationalisation

## Credits

- [Google's Material Symbols](https://fonts.google.com/icons) for the SVG icons
- [Google Fonts](https://fonts.google.com/) for the Roboto font
