import requests
import os


def get_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ValueError(f"{name} is not set")
    return value


YOUTRACK_URL = get_env("YOUTRACK_URL")
YOUTRACK_TOKEN = get_env("YOUTRACK_TOKEN")

youtrack_session = requests.Session()
youtrack_session.headers.update({"Authorization": f"Bearer {YOUTRACK_TOKEN}"})

issues_list = youtrack_session.get(f"{YOUTRACK_URL}api/issues").json()

print(f"Found {len(issues_list)} issues")
