#utils.py
""" this file_path open the json file"""
import inspect
import json
from pathlib import Path
config_cache=None

def open_json(section=None):
    """ 1.Detects and loads any JSON file inside the /config folder.
        2.Auto-detects which section (e.g., mysql/email/ssh) to return
        based on the calling module.
       3.Caches the config so it's loaded only once per run. """

    global config_cache
    json_files=[]
    config_path=None
    if config_cache is None:
        current_file=Path(__file__).resolve()
        project_root=current_file.parents[1]
        config_dir=project_root/"config"

        json_files=list(config_dir.glob("*.json"))
        if not json_files:
            raise FileNotFoundError(" [ERROR] No json config file found in /config")

        if len(json_files)==1:
            config_path=json_files[0]
            print(f"detected config file is {config_path.name}")
        else:
            print("multiple config files found")
            for i,file in enumerate(json_files,1):
                print(f"{i}.{file.name}")
            try:
                choice=int(input("enter number to select the config_file:"))
                config_path=json_files[choice-1]
            except (ValueError, IndexError):
                print("[WARN] Invalid input. Defaulting to first config file.")
                config_path = json_files[0]

        if config_path is None:
            config_path = json_files[0]
            print(f"[WARN] Defaulting to first config file: {config_path.name}")

        with open(config_path,"r",encoding="utf-8") as f:
            config_cache=json.load(f)

    if section is None:
        # Find which module (file) called open_json()
        caller = inspect.stack()[1].filename  # e.g., /lib/sql.py
        caller_name = Path(caller).stem.lower()  # extract 'sql'

        mapping = {
            "sql": "mysql",
            "emailer": "email",
            "ssh": "ssh",
            "rest": "api",
        }

        section = mapping.get(caller_name)

    if section:
        if section in config_cache:
            return config_cache[section]
        else:
            raise KeyError(f" [error] Section '{section}' not found in config file.")
    else:
        return config_cache

def get_config(section=None):
    """
    Shortcut for open_json(); kept for readability.
    Usage:
        get_config("mysql") or get_config("email")
    """
    return open_json(section)

def get_project_root() -> Path:
    """Return the absolute path of the project root."""
    return Path(__file__).resolve().parents[1]

def get_reports_dir() -> Path:
    """Return (and create if missing) the /reports directory path."""
    reports_dir = get_project_root() / "reports"
    reports_dir.mkdir(exist_ok=True)
    return reports_dir