# vaillant-poller

Script to poll the Vaillant API, fetch heating system state, persist the data to local files and push to a metrics server.

## Install dependencies

`pip install -r requirements.txt`

## Run

Set the environment variables:

- VAILLANT_USER
- VAILLANT_PASSWORD
- VAILLANT_POLL_DELAY_SECONDS
- VAILLANT_LOCAL_STORAGE_PATH
- VAILLANT_METRICS_URL
- VAILLANT_METRICS_API_KEY

`python3 script.py`

## Release

This script is published to Docker Hub, which I use to deploy to a Raspberry Pi. To release a new version run:

```
docker build -t timsummertonbrier/vaillant-poller .
docker push timsummertonbrier/vaillant-poller
```

Once the new version has been pushed, [follow the instructions here](https://github.com/sizlo/raspberry-pi-config?tab=readme-ov-file#app-updates) to get the new version running on the Raspberry Pi.