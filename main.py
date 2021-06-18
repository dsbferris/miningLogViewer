from datetime import datetime, timedelta
import requests
from classes import ShareClass, LogEvalClass
from phoenix_log_viewer import analyse_phoenix_log
from nanominer_log_viewer import analyse_nano_log
from pathlib import Path
import os

from colorama import init, Fore

init()


# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET


def get_all_log_files_from_directory(root_dir: Path) -> list[Path]:
    return list(root_dir.rglob("*.*"))


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


def add_payout_stats(log_eval_list: list[LogEvalClass]) -> list[LogEvalClass]:
    sorted_eval_list: list[LogEvalClass] = [log_eval_list[0]]
    for i in range(1, len(log_eval_list)):
        current_eval = log_eval_list[i]
        if current_eval.payout_worked_for == sorted_eval_list[-1].payout_worked_for:
            sorted_eval_list[-1] += current_eval
        else:
            sorted_eval_list.append(current_eval)

    return sorted_eval_list


def run_phoenix(payout_dates: list[datetime], root_path: Path):
    kwh_price = 0.3
    wattage = 170

    ferris_phoenix_list: list[LogEvalClass] = []
    print("Phoenixminer: ")
    all_log_files = get_all_log_files_from_directory(root_path)
    for path in all_log_files:
        ferris_phoenix_list += analyse_phoenix_log(path, payout_dates)

    print("\n")
    ferris_phoenix_list = add_payout_stats(ferris_phoenix_list)
    for e in ferris_phoenix_list:
        print(f"{Fore.GREEN}{e}\n{e.get_power_cost_string(wattage=wattage, kwh_price=kwh_price)}{Fore.RESET}")

    print("\nTotal:")
    total: LogEvalClass = ferris_phoenix_list[0]
    for i in range(1, len(ferris_phoenix_list)):
        total += ferris_phoenix_list[i]
    total.payout_worked_for = datetime.min
    print(f"{total}\n{total.get_power_cost_string(wattage=wattage, kwh_price=kwh_price)}")


def run_nano(payout_dates: list[datetime], root_path: Path):
    kwh_price = 0.3
    wattage = 170

    eval_list: list[LogEvalClass] = []
    print("Nanominer: ")
    all_log_files = get_all_log_files_from_directory(root_path)
    for path in all_log_files:
        log_eval = analyse_nano_log(path, payout_dates)
        if log_eval[1]:
            if len(log_eval[0]) == 1:
                eval_list[-1].shares = log_eval[0][0].shares
                eval_list[-1].runtime += log_eval[0][0].runtime
            else:
                raise("YOUR WORST NIGHTMARE!")
        else:
            eval_list += log_eval[0]
    del log_eval, path

    print("\n")
    eval_list = add_payout_stats(eval_list)
    for e in eval_list:
        print(f"{Fore.GREEN}{e}\n{e.get_power_cost_string(wattage=wattage, kwh_price=kwh_price)}{Fore.RESET}")

    print("\nTotal:")
    total: LogEvalClass = eval_list[0]
    for i in range(1, len(eval_list)):
        total += eval_list[i]
    total.payout_worked_for = datetime.min
    print(f"{total}\n{total.get_power_cost_string(wattage=wattage, kwh_price=kwh_price)}")


def start():
    ferris_phoenix = Path(os.path.join(Path.home(), r"OneDrive\logs\ferris_phoenix"))
    ferris_nano = Path(os.path.join(Path.home(), r"OneDrive\logs\ferris_nano"))
    levin = Path(os.path.join(Path.home(), r"OneDrive\logs\levin"))
    levin_new = Path(os.path.join(Path.home(), r"OneDrive\logs\levin_new"))

    payout_dates = get_nanopool_payout_dates()
    payout_dates.append(datetime.max)  # For next upcoming payout

    # run_phoenix(payout_dates, ferris_phoenix)
    run_nano(payout_dates, levin_new)


start()
