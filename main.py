from datetime import datetime, timedelta
import requests
import pathlib
from classes import ShareClass, LogEvalClass
from phoenix_log_viewer import analyse_phoenix_log

from colorama import init, Fore

init()
# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET


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


def sum_log_evals(log_eval_list: list[LogEvalClass]) -> list[LogEvalClass]:
    sorted_eval_list: list[LogEvalClass] = [log_eval_list[0]]
    for i in range(1, len(log_eval_list)):
        current_eval = log_eval_list[i]
        if current_eval.payout_worked_for == sorted_eval_list[-1].payout_worked_for:
            sorted_eval_list[-1] += current_eval
        else:
            sorted_eval_list.append(current_eval)

    return sorted_eval_list


def start():
    levin_new_nano_root_path = r"logs\original_logs\levin_nanominer_logs\levin_new"
    ferris_nano_root_path = r"logs\original_logs\nanominer"

    payout_dates = get_nanopool_payout_dates()
    payout_dates.append(datetime.max)  # For next upcoming payout

    ferris_phoenix_root_path = r"logs\original_logs\phoenixminer"
    ferris_phoenix_list: list[LogEvalClass] = []
    print("Ferris Phoenixminer: ")
    all_log_files = get_all_log_files_from_directory(ferris_phoenix_root_path)
    for path in all_log_files:
        ferris_phoenix_list += analyse_phoenix_log(path, payout_dates)

    print("\n")
    ferris_phoenix_list = sum_log_evals(ferris_phoenix_list)
    for e in ferris_phoenix_list:
        print(f"{Fore.GREEN}"
              f"{e}\n"
              f"At 170W & 0,30€/KWh: {e.get_power_cost(wattage=170, cost_per_kwh_in_eur=0.3)}€"
              f"{Fore.RESET}")

    print("\nTotal:")
    total: LogEvalClass = ferris_phoenix_list[0]
    for i in range(1, len(ferris_phoenix_list)):
        total += ferris_phoenix_list[i]
    total.payout_worked_for = datetime.min
    print(f"{total}\n"
          f"At 170W & 0,30€/KWh: {total.get_power_cost(wattage=170, cost_per_kwh_in_eur=0.3)}€")
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
