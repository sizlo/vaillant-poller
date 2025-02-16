# vaillant-poller

Script to poll the Vaillant API, fetch heating system state and energy usage, persist the data to local files and push to a metrics server.

## Install dependencies

`pip install -r requirements.txt`

## Run

Set the environment variables:

- VAILLANT_USER
- VAILLANT_PASSWORD
- VAILLANT_POLL_DELAY_SECONDS
- VAILLANT_LOCAL_STORAGE_PATH

`python3 script.py`
