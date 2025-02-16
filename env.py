import sys
import os


def require_env(key):
    if key in os.environ.keys():
        return os.environ[key]
    print(f"Missing required environment variable: {key}", file=sys.stderr)
    sys.exit(1)

