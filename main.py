from datetime import datetime, timedelta
import requests
import pathlib
from classes import ShareClass, LogEvalClass
from phoenix_log_viewer import analyse_phoenix_log


def get_all_log_files_from_directory(root_dir: str) -> list[pathlib.Path]:
    return list(pathlib.Path(root_dir).rglob("*.*"))


def get_nanopool_payout_dates() -> list[datetime]:
    response = requests.get("https://api.nanopool.org/v1/eth/payments/0x88276b6528b600e290f0c4598162aa31e0d30639")
    dates = []
    if response.ok:
        json = response.json()
        payout_data = json.get("data")
        for data in reversed(payout_data):
            dates.append(datetime.fromtimestamp(data.get("date")))
        del json, payout_data, response, data
    return dates


def get_nanopool_worker_ratings() -> list[dict]:
    response = requests.get("https://api.nanopool.org/v1/eth/workers/0x88276b6528b600e290f0c4598162aa31e0d30639")
    workers: list[dict] = []
    if response.ok:
        json = response.json()
        json_data = json.get("data")
        for worker in json_data:
            workers.append(dict(name=worker["id"], rating=worker["rating"]))
        del json, json_data, response, worker
    return workers


def start():
    levin_new_nano_root_path = r"logs\original_logs\levin_nanominer_logs\levin_new"
    ferris_nano_root_path = r"logs\original_logs\nanominer"

    payout_dates = get_nanopool_payout_dates()
    payout_dates.append(datetime.max)  # For next upcoming payout

    ferris_phoenix_root_path = r"logs\original_logs\phoenixminer"
    ferris_phoenix_list: list[LogEvalClass] = []
    print("Ferris Phoenixminer: ")
    for path in get_all_log_files_from_directory(ferris_phoenix_root_path):
        ferris_phoenix_list += analyse_phoenix_log(path, payout_dates)

    print("\n\n")

    exit(0)

    # levin_list: list[LogEvalClass] = []
    # print("Levin Nanominer:")
    # for path in get_all_log_files_from_directory(levin_new_nano_root_path):
    #     levin_list += analyse_nano_log(path, payout_dates)
    #
    # print("\n\n")
    #
    # ferris_nano_list: list[LogEvalClass] = []
    # print("Ferris Nanominer: ")
    # for path in get_all_log_files_from_directory(ferris_nano_root_path):
    #     ferris_nano_list += analyse_nano_log(path, payout_dates)


start()
