# Home Assistant REST API Reference

Source: https://developers.home-assistant.io/docs/api/rest/
Saved: 2026-06-14

## Overview

Home Assistant provides a RESTful API on the same port as the web frontend (default port is port 8123). The API accepts and returns only JSON-encoded objects.

### Prerequisites

- If the frontend integration isn't active, add the API integration to `configuration.yaml`
- All API calls require the header: `Authorization: Bearer TOKEN`
- Obtain a Long-Lived Access Token from your profile at `http://IP_ADDRESS:8123/profile`

### Base Endpoints

- Control interface: `http://IP_ADDRESS:8123/`
- RESTful API: `http://IP_ADDRESS:8123/api/`

## Client Examples

### Using cURL
```bash
curl \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  http://IP_ADDRESS:8123/ENDPOINT
```

### Using Python
```python
from requests import get

url = "http://localhost:8123/ENDPOINT"
headers = {
    "Authorization": "Bearer TOKEN",
    "content-type": "application/json",
}

response = get(url, headers=headers)
print(response.text)
```

### Using RESTful Command Integration
```yaml
turn_light_on:
  url: http://localhost:8123/api/states/light.study_light
  method: POST
  headers:
    authorization: 'Bearer TOKEN'
    content-type: 'application/json'
  payload: '{"state":"on"}'
```

## Status Codes

Successful calls return 200 or 201. Other possible codes:
- 400 (Bad Request)
- 401 (Unauthorized)
- 404 (Not Found)
- 405 (Method Not Allowed)

---

## API Endpoints

### GET `/api/`

Returns a message if the API is operational.

**Response:**
```json
{
  "message": "API running."
}
```

**cURL:**
```bash
curl \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  http://localhost:8123/api/
```

**Note:** make sure you include the trailing `/`, the full path is `/api/`, NOT `/api`

---

### GET `/api/config`

Returns the current configuration as JSON.

**Response Example:**
```json
{
   "components":[
      "sensor.cpuspeed",
      "frontend",
      "config.core",
      "http",
      "map",
      "api",
      "sun",
      "config",
      "discovery",
      "conversation",
      "recorder",
      "group",
      "sensor",
      "websocket_api",
      "automation",
      "config.automation",
      "config.customize"
   ],
   "config_dir":"/home/ha/.homeassistant",
   "elevation":510,
   "latitude":45.8781529,
   "location_name":"Home",
   "longitude":8.458853651,
   "time_zone":"Europe/Zurich",
   "unit_system":{
      "length":"km",
      "mass":"g",
      "temperature":"°C",
      "volume":"L"
   },
   "version":"0.56.2",
   "whitelist_external_dirs":[
      "/home/ha/.homeassistant/www",
      "/home/ha/.homeassistant/"
   ]
}
```

**cURL:**
```bash
curl \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  http://localhost:8123/api/config
```

---

### GET `/api/components`

Returns a list of currently loaded components.

**Response Example:**
```json
[
  "currentcost.sensor",
  "tapo.switch",
  "tuya_ble.sensor",
  "backup",
  "ble_monitor.binary_sensor",
  "localtuya.remote",
  "logger",
  "http",
  "hacs",
  "cast",
  "device_tracker",
  "upnp.binary_sensor",
  "notify",
  "person",
  "..."
]
```

**cURL:**
```bash
curl \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  http://localhost:8123/api/components
```

---

### GET `/api/events`

Returns an array of event objects. Each event object contains event name and listener count.

**Response Example:**
```json
[
    {
      "event": "state_changed",
      "listener_count": 5
    },
    {
      "event": "time_changed",
      "listener_count": 2
    }
]
```

**cURL:**
```bash
curl \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  http://localhost:8123/api/events
```

---

### GET `/api/services`

Returns an array of service objects. Each object contains the domain and which services it contains.

**Response Example:**
```json
[
    {
      "domain": "browser",
      "services": [
        "browse_url"
      ]
    },
    {
      "domain": "keyboard",
      "services": [
        "volume_up",
        "volume_down"
      ]
    }
]
```

**cURL:**
```bash
curl \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  http://localhost:8123/api/services
```

---

### GET `/api/history/period/<timestamp>`

Returns an array of state changes in the past. Each object contains further details for the entities.

The `<timestamp>` (format: `YYYY-MM-DDThh:mm:ssTZD`) is optional and defaults to 1 day before request time.

**Required Parameters:**
- `filter_entity_id=<entity_ids>` — filter by one or more entities (comma-separated)

**Optional Parameters:**
- `end_time=<timestamp>` — choose period end (URL encoded; defaults to 1 day)
- `minimal_response` — return only `last_changed` and `state` (faster)
- `no_attributes` — skip attributes from database (faster)
- `significant_changes_only` — return only significant state changes

**Response Example (without minimal_response):**
```json
[
    [
        {
            "attributes": {
                "friendly_name": "Weather Temperature",
                "unit_of_measurement": "°C"
            },
            "entity_id": "sensor.weather_temperature",
            "last_changed": "2016-02-06T22:15:00+00:00",
            "last_updated": "2016-02-06T22:15:00+00:00",
            "state": "-3.9"
        },
        {
            "attributes": {
                "friendly_name": "Weather Temperature",
                "unit_of_measurement": "°C"
            },
            "entity_id": "sensor.weather_temperature",
            "last_changed": "2016-02-06T22:15:00+00:00",
            "last_updated": "2016-02-06T22:15:00+00:00",
            "state": "-1.9"
        }
    ]
]
```

**Response Example (with minimal_response):**
```json
[
    [
        {
            "attributes": {
                "friendly_name": "Weather Temperature",
                "unit_of_measurement": "°C"
            },
            "entity_id": "sensor.weather_temperature",
            "last_changed": "2016-02-06T22:15:00+00:00",
            "last_updated": "2016-02-06T22:15:00+00:00",
            "state": "-3.9"
        },
        {
            "last_changed": "2016-02-06T22:20:00+00:00",
            "state": "-2.9"
        },
        {
            "last_changed": "2016-02-06T22:22:00+00:00",
            "state": "-2.2"
        },
        {
            "attributes": {
                "friendly_name": "Weather Temperature",
                "unit_of_measurement": "°C"
            },
            "entity_id": "sensor.weather_temperature",
            "last_changed": "2016-02-06T22:25:00+00:00",
            "last_updated": "2016-02-06T22:25:00+00:00",
            "state": "-1.9"
        }
    ]
]
```

**cURL Examples:**

Past day history (default):
```bash
curl \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  "http://localhost:8123/api/history/period?filter_entity_id=sensor.temperature"
```

Minimal history with manual start date:
```bash
curl \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  "http://localhost:8123/api/history/period/2023-09-04T00:00:00+02:00?filter_entity_id=sensor.temperature,sensor.kitchen_temperature&minimal_response"
```

History with specific date range:
```bash
curl \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  "http://localhost:8123/api/history/period/2021-09-04T00%3A00%3A00%2B02%3A00?end_time=2023-09-04T00%3A00%3A00%2B02%3A00&filter_entity_id=sensor.temperature"
```

---

### GET `/api/logbook/<timestamp>`

Returns an array of logbook entries.

The `<timestamp>` (format: `YYYY-MM-DDThh:mm:ssTZD`) is optional and defaults to 1 day before request time.

**Optional Parameters:**
- `entity=<entity_id>` — filter by one entity
- `end_time=<timestamp>` — choose period end (URL encoded)

**Response Example:**
```json
[
  {
    "context_user_id": null,
    "domain": "alarm_control_panel",
    "entity_id": "alarm_control_panel.area_001",
    "message": "changed to disarmed",
    "name": "Security",
    "when": "2020-06-20T16:44:26.127295+00:00"
  },
  {
    "context_user_id": null,
    "domain": "homekit",
    "entity_id": "alarm_control_panel.area_001",
    "message": "send command alarm_arm_night for Security",
    "name": "HomeKit",
    "when": "2020-06-21T02:59:05.759645+00:00"
  },
  {
    "context_user_id": null,
    "domain": "alarm_control_panel",
    "entity_id": "alarm_control_panel.area_001",
    "message": "changed to armed_night",
    "name": "Security",
    "when": "2020-06-21T02:59:06.015463+00:00"
  }
]
```

**cURL Examples:**

Basic logbook:
```bash
curl \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  http://localhost:8123/api/logbook/2016-12-29T00:00:00+02:00
```

With end time and entity filter:
```bash
curl \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  "http://localhost:8123/api/logbook/2016-12-29T00:00:00+02:00?end_time=2099-12-31T00%3A00%3A00%2B02%3A00&entity=sensor.temperature"
```

With end time only:
```bash
curl \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  "http://localhost:8123/api/logbook/2016-12-29T00:00:00+02:00?end_time=2099-12-31T00%3A00%3A00%2B02%3A00"
```

---

### GET `/api/states`

Returns an array of state objects. Each state has the following attributes: `entity_id`, `state`, `last_changed` and `attributes`.

**Response Example:**
```json
[
    {
        "attributes": {},
        "entity_id": "sun.sun",
        "last_changed": "2016-05-30T21:43:32.418320+00:00",
        "state": "below_horizon"
    },
    {
        "attributes": {},
        "entity_id": "process.Dropbox",
        "last_changed": "22016-05-30T21:43:32.418320+00:00",
        "state": "on"
    }
]
```

**cURL:**
```bash
curl \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  http://localhost:8123/api/states
```

---

### GET `/api/states/<entity_id>`

Returns a state object for specified `entity_id`. Returns 404 if not found.

**Response Example:**
```json
{
   "attributes":{
      "azimuth":336.34,
      "elevation":-17.67,
      "friendly_name":"Sun",
      "next_rising":"2016-05-31T03:39:14+00:00",
      "next_setting":"2016-05-31T19:16:42+00:00"
   },
   "entity_id":"sun.sun",
   "last_changed":"2016-05-30T21:43:29.204838+00:00",
   "last_updated":"2016-05-30T21:50:30.529465+00:00",
   "state":"below_horizon"
}
```

**cURL:**
```bash
curl \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  http://localhost:8123/api/states/sensor.kitchen_temperature
```

---

### GET `/api/error_log`

Retrieve all errors logged during the current session of Home Assistant as a plaintext response.

**Response Example:**
```
15-12-20 11:02:50 homeassistant.components.recorder: Found unfinished sessions
15-12-20 11:03:03 netdisco.ssdp: Error fetching description at http://192.168.1.1:8200/rootDesc.xml
15-12-20 11:04:36 homeassistant.components.alexa: Received unknown intent HelpIntent
```

**cURL:**
```bash
curl \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  http://localhost:8123/api/error_log
```

---

### GET `/api/camera_proxy/<camera entity_id>`

Returns the data (image) from the specified camera `entity_id`.

**cURL:**
```bash
curl \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -o image.jpg \
  "http://localhost:8123/api/camera_proxy/camera.my_sample_camera?time=1462653861261"
```

---

### GET `/api/calendars`

Returns the list of calendar entities.

**Response Example:**
```json
[
  {
    "entity_id": "calendar.holidays",
    "name": "National Holidays"
  },
  {
    "entity_id": "calendar.personal",
    "name": "Personal Calendar"
  }
]
```

**cURL:**
```bash
curl \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  http://localhost:8123/api/calendars
```

---

### GET `/api/calendars/<calendar entity_id>?start=<timestamp>&end=<timestamp>`

Returns the list of calendar events for the specified calendar `entity_id` between the `start` and `end` times (exclusive).

The events in the response have a `start` and `end` that contain either `dateTime` or `date` for an all day event.

**Response Example:**
```json
[
  {
    "summary": "Cinco de Mayo",
    "start": {
      "date": "2022-05-05"
    },
    "end": {
      "date": "2022-05-06"
    }
  },
  {
    "summary": "Birthday Party",
    "start": {
      "dateTime": "2022-05-06T20:00:00-07:00"
    },
    "end": {
      "dateTime": "2022-05-06T23:00:00-07:00"
    },
    "description": "Don't forget to bring balloons",
    "location": "Brian's House"
  }
]
```

**cURL:**
```bash
curl \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  "http://localhost:8123/api/calendars/calendar.holidays?start=2022-05-01T07:00:00.000Z&end=2022-06-12T07:00:00.000Z"
```

---

### POST `/api/states/<entity_id>`

Updates or creates a state. You can create any state that you want, it does not have to be backed by an entity in Home Assistant.

**Note:** This endpoint sets the representation of a device within Home Assistant and will not communicate with the actual device. To communicate with the device, use the `POST /api/services/<domain>/<service>` endpoint.

Expects a JSON object with at least a state attribute:

**Request Example:**
```json
{
    "state": "below_horizon",
    "attributes": {
        "next_rising":"2016-05-31T03:39:14+00:00",
        "next_setting":"2016-05-31T19:16:42+00:00"
    }
}
```

Returns 200 if entity existed, 201 if new state was created. Response body contains JSON-encoded State object:

**Response Example:**
```json
{
    "attributes": {
        "next_rising":"2016-05-31T03:39:14+00:00",
        "next_setting":"2016-05-31T19:16:42+00:00"
    },
    "entity_id": "sun.sun",
    "last_changed": "2016-05-30T21:43:29.204838+00:00",
    "last_updated": "2016-05-30T21:47:30.533530+00:00",
    "state": "below_horizon"
}
```

**cURL:**
```bash
curl \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"state": "25", "attributes": {"unit_of_measurement": "°C"}}' \
  http://localhost:8123/api/states/sensor.kitchen_temperature
```

**Python Example:**
```python
from requests import post

url = "http://localhost:8123/api/states/sensor.kitchen_temperature"
headers = {"Authorization": "Bearer TOKEN", "content-type": "application/json"}
data = {"state": "25", "attributes": {"unit_of_measurement": "°C"}}

response = post(url, headers=headers, json=data)
print(response.text)
```

---

### POST `/api/events/<event_type>`

Fires an event with `event_type`.

Can pass an optional JSON object as `event_data`:

**Request Example:**
```json
{
    "next_rising":"2016-05-31T03:39:14+00:00"
}
```

Returns a message if successful:

**Response Example:**
```json
{
    "message": "Event download_file fired."
}
```

---

### POST `/api/services/<domain>/<service>`

Calls a service within a specific domain. Will return when the service has been executed.

Can pass an optional JSON object as `service_data`:

**Request Example:**
```json
{
    "entity_id": "light.Ceiling"
}
```

Returns a list of states that changed while the service was executed:

**Response Example (without return_response):**
```json
[
    {
        "attributes": {},
        "entity_id": "sun.sun",
        "last_changed": "2016-05-30T21:43:32.418320+00:00",
        "state": "below_horizon"
    },
    {
        "attributes": {},
        "entity_id": "process.Dropbox",
        "last_changed": "22016-05-30T21:43:32.418320+00:00",
        "state": "on"
    }
]
```

**Response Example (with ?return_response):**
```json
{
    "changed_states": [
        {
            "attributes": {},
            "entity_id": "sun.sun",
            "last_changed": "2024-04-22T20:45:54.418320-04:00",
            "state": "below_horizon"
        },
        {
            "attributes": {},
            "entity_id": "binary_sensor.dropbox",
            "last_changed": "2024-04-22T20:45:54.418320-04:00",
            "state": "on"
        }
    ],
    "service_response": {
        "weather.new_york_forecast": {
            "forecast": [
                {
                    "condition": "clear-night",
                    "datetime": "2024-04-22T20:45:55.173725-04:00",
                    "precipitation_probability": 0,
                    "temperature": null,
                    "templow": 6.0
                },
                {
                    "condition": "rainy",
                    "datetime": "2024-04-23T20:45:55.173756-04:00",
                    "precipitation_probability": 60,
                    "temperature": 16.0,
                    "templow": 4.0
                }
            ]
        }
    }
}
```

**Note:** The result will include any states that changed while the service was being executed, even if their change was the result of something else happening in the system.

If the service supports returning response data, add `?return_response` to the URL.

**Important:** Some services return no data, others optionally return response data, and some always return response data. If you don't use `return_response` when calling a service that must return data, the API will return a 400. Similarly, you will receive a 400 if you use `return_response` when calling a service that doesn't return any data.

**cURL Examples:**

Turn light on:
```bash
curl \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "switch.christmas_lights"}' \
  http://localhost:8123/api/services/switch/turn_on
```

**Python Example:**

Turn light on:
```python
from requests import post

url = "http://localhost:8123/api/services/light/turn_on"
headers = {"Authorization": "Bearer TOKEN"}
data = {"entity_id": "light.study_light"}

response = post(url, headers=headers, json=data)
print(response.text)
```

Send MQTT message:
```bash
curl \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"payload": "OFF", "topic": "home/fridge", "retain": "True"}' \
  http://localhost:8123/api/services/mqtt/publish
```

Retrieve daily weather forecast:
```bash
curl \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"entity_id": "weather.forecast_home", "type": "daily"}' \
  http://localhost:8123/api/services/weather/get_forecasts?return_response
```

---

### POST `/api/template`

Render a Home Assistant template.

**Request Example:**
```json
{
    "template": "Paulus is at {{ states('device_tracker.paulus') }}!"
}
```

Returns the rendered template in plain text:

**Response Example:**
```
Paulus is at work!
```

**cURL:**
```bash
curl \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"template": "It is {{ now() }}!"}' \
  http://localhost:8123/api/template
```

---

### POST `/api/config/core/check_config`

Trigger a check of `configuration.yaml`. No additional data needs to be passed in with this request. Needs config integration enabled.

If successful:

**Response Example:**
```json
{
    "errors": null,
    "result": "valid"
}
```

If unsuccessful, the errors attribute lists what caused failure:

**Response Example:**
```json
{
    "errors": "Integration not found: frontend:",
    "result": "invalid"
}
```

---

### POST `/api/intent/handle`

Handle an intent.

You must add `intent:` to your `configuration.yaml` to enable this endpoint.

**cURL Example:**
```bash
curl \
  -H "Authorization: Bearer TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{ "name": "SetTimer", "data": { "seconds": "30" } }' \
  http://localhost:8123/api/intent/handle
```

---

### DELETE `/api/states/<entity_id>`

Deletes an entity with the specified `entity_id`.

**cURL:**
```bash
curl \
  -X DELETE \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  http://localhost:8123/api/states/sensor.kitchen_temperature
```
