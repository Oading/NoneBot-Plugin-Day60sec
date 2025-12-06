import requests
import yaml
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent


def fetch_and_save_json():

    config_path = BASE_DIR / "config.yaml"
    with config_path.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    url = config["url"]
    querystring = config["querystring"]
    headers = config["headers"]
    response = requests.get(url, headers=headers, params=querystring)
    tempdata = response.json()
    archive_path_json = BASE_DIR / "archive/json"
    archive_path_json.mkdir(parents=True, exist_ok=True)
    file_path = archive_path_json / \
        f"{datetime.now().strftime('%Y-%m-%d')}.json"
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(tempdata, f, ensure_ascii=False, indent=2)

    return file_path
