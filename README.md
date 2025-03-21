# vaillant-poller

Script to poll the Vaillant API, fetch heating system state and energy consumption data, persist the data to local files and expose prometheus metrics. Metrics are also pushed to a remote metrics collector, but I intend to remove this and replace it with the prometheus remote write feature.

> [!WARNING]  
> The Vaillant API enforces a quota on the endpoint to get energy consumption data. If this quota is exceeded then the entire household is blocked from requesting energy consumption data for a period of time. This means you cannot view the usage graphs in the app.
> The script is set up to call the endpoint once a day in normal use, but if previous days are missing it will fill those gaps. If there are a lot of days missing this makes it more likely to hit the quota limit. The `VAILLANT_CONSUMPTION_LOOKBACK_DAYS` environment variable controls how many days in the past the script will fill.

## Install dependencies

`pip install -r requirements.txt`

## Run

Set the environment variables:

- VAILLANT_USER
- VAILLANT_PASSWORD
- VAILLANT_POLL_DELAY_SECONDS
- VAILLANT_LOCAL_STORAGE_PATH
- VAILLANT_NUM_DAILY_SYSTEM_DUMPS_TO_KEEP
- VAILLANT_CONSUMPTION_LOOKBACK_DAYS
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