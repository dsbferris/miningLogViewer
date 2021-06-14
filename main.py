import os
import decimal
from datetime import datetime, timedelta
import requests
import pathlib
from sub_classes import phoenix_log_viewer as phoenix, nanominer_log_viewer as nano


class ShareClass(object):
    total_shares: int
    accepted_shares: int
    rejected_shares: int

    def __init__(self, total=0, accepted=0, rejected=0):
        self.total_shares = total
        self.accepted_shares = accepted
        self.rejected_shares = rejected

    def __add__(self, other):
        total = self.total_shares + other.total_shares
        accepted = self.accepted_shares + other.accepted_shares
        rejected = self.rejected_shares + other.rejected_shares
        return ShareClass(total, accepted, rejected)

    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return self.__add__(other)

    def __str__(self):
        return f"Total: {self.total_shares} (Accepted: {self.accepted_shares}/Rejected: {self.rejected_shares})"


class LogEvalClass:
    payout_worked_for: datetime
    worker_name: str
    runtime: timedelta
    shares: ShareClass

    def __init__(self, payout_worked_for: datetime = datetime.min, worker_name="Default", runtime=timedelta(0),
                 shares: ShareClass = ShareClass()):
        self.payout_worked_for = payout_worked_for
        self.shares = shares
        self.worker_name = worker_name
        self.runtime = runtime

    def get_power_cost(self, wattage: int, cost_per_kwh_in_eur: decimal) -> decimal:
        hours = self.runtime.total_seconds() / 3600
        kilo_wattage = wattage / 1000
        kwh = kilo_wattage * hours
        cost = kwh * cost_per_kwh_in_eur
        return cost

    def __str__(self):
        return f"Payout {self.payout_worked_for} "



def get_all_log_files_from_directory(root_dir: str) -> list[pathlib.Path]:
    return list(pathlib.Path(root_dir).rglob("*.*"))


def get_nanopool_payout_dates() -> list[datetime]:
    response = requests.get("https://api.nanopool.org/v1/eth/payments/0x88276b6528b600e290f0c4598162aa31e0d30639")
    payout_dates = []
    if response.ok:
        json = response.json()
        payout_data = json.get("data")
        for data in reversed(payout_data):
            payout_dates.append(datetime.fromtimestamp(data.get("date")))
        del json, payout_data, response, data
    return payout_dates


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


levin_new_nano_root_path = r"logs\original_logs\levin_nanominer_logs\levin_new"
ferris_nano_root_path = r"logs\original_logs\nanominer"
ferris_phoenix_root_path = r"logs\original_logs\phoenixminer"

LogEvalList: list[LogEvalClass] = [LogEvalClass(),
                                   LogEvalClass(payout_worked_for=datetime.max, worker_name="sample", runtime=timedelta(seconds=120),
                                                total=10, accepted=8, rejected=2)
                                   ]


# region Runtime analysis


# Prints out used KW/h and total cost in € for given values
def print_statistics(total_seconds: int, wattage: int, price: float):
    total_hours = total_seconds / 3600
    kwh = total_hours * (wattage / 1000)
    total_seconds, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(total_seconds, 60)
    days, hours = divmod(hours, 24)
    print("%d Days, %dh:%02dm:%02ds" % (days, hours, minutes, seconds))

    kwh = total_hours * (wattage / 1000)
    print("\033[1m At %dW & %.4f€/KWh: \033[4m%.4fKWh\033[0m, \033[4m%.4f€\033[0m\033[0m"
          % (wattage, price, kwh, kwh * price))


def get_nanominer():
    wattage = 170
    for i in range(2, 7):
        print(f"Month: {i}")
        if i >= 4:
            price = 0.298
        else:
            price = 0.2735

        nanominer_log_path = rf"C:\Users\Ferris\PycharmProjects\pythonProject\logs\original_logs\nanominer\{i:02d}"
        if os.path.exists(nanominer_log_path):
            nanominer_total_seconds = nano.get_total_seconds(nanominer_log_path)
            print_statistics(nanominer_total_seconds, wattage, price)
            nano.find_possible_errors(nanominer_log_path, "8192 MB available")
            print("\n")
        else:
            print(f"log_path does not exists: \n{nanominer_log_path}")


def get_nanominer_levin():
    wattage = 170
    price = 0.3
    nanominer_log_path = r"logs/original_logs/levin_nanominer_logs/logs"
    if os.path.exists(nanominer_log_path):
        nanominer_total_seconds = nano.get_total_seconds(nanominer_log_path)
        print_statistics(nanominer_total_seconds, wattage, price)
        nano.find_possible_errors(nanominer_log_path, "8192 MB available")
        print("\n")
    else:
        print(f"log_path does not exists: \n{nanominer_log_path}")


def get_phoenix_miner():
    wattage = 170
    for i in range(2, 7):
        print(f"Month: {i}")
        if i >= 4:
            price = 0.298
        else:
            price = 0.2735

        phoenix_log_path = rf"logs\original_logs\phoenixminer\{i:02d}"
        if os.path.exists(phoenix_log_path):
            phoenix_total_seconds = phoenix._get_all_logs_total_seconds(phoenix_log_path)
            print_statistics(phoenix_total_seconds, wattage, price)
            print("\n")
        else:
            print(f"log_path does not exists: \n{phoenix_log_path}")


def read_my_logs():
    print("Nanominer:")
    get_nanominer()

    print("Phoenixminer:")
    get_phoenix_miner()

# endregion
