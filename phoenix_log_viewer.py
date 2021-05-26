import os
import datetime


def get_log_runtime(log_file_path):
    with open(log_file_path, "r") as log_file:
        log_file_text = log_file.read()
    split = log_file_text.splitlines(False)
    first_line = split[0]
    last_line = split[-1]
    first_line_time = first_line.split(" ")[0].removesuffix(":")
    last_line_time = last_line.split(" ")[0].removesuffix(":")
    first_timestamp = datetime.datetime.strptime(first_line_time, '%Y.%m.%d:%H:%M:%S.%f')
    last_timestamp = datetime.datetime.strptime(last_line_time, '%Y.%m.%d:%H:%M:%S.%f')
    delta = last_timestamp - first_timestamp
    return delta


def get_all_logs_total_seconds(log_path) -> float:
    delta_sum = datetime.timedelta(0)
    files = os.listdir(log_path)
    for file in files:
        file_path = os.path.join(log_path, file)
        delta_sum += get_log_runtime(file_path)
    return delta_sum.total_seconds()


def get_total_shares_in_time(log_path, start_time, end_time) -> int:
    total_shares = 0
    files = os.listdir(log_path)
    for file in files:
        log_file_path = os.path.join(log_path, file)
        with open(log_file_path, "r") as log_file:
            log_file_text = log_file.read()
        if log_file_text.find("shares: ") == -1:
            continue    # falls direkt gestartet und beendet wurde
        # 2021.05.11:10:53:31.154: main Eth speed: 55.217 MH/s, shares: 322/0/2, time: 14:22
        # total shares/rejected shares/incorrect shares
        # shares: 0/0/0,

    return 0


def phoenix_total_shares():
    import requests
    import datetime
    response = requests.get("https://api.nanopool.org/v1/eth/payments/0x88276b6528b600e290f0c4598162aa31e0d30639")
    dates = []
    if response.ok:
        json = response.json()
        payout_data = json.get("data")
        for data in reversed(payout_data):
            dates.append(datetime.datetime.fromtimestamp(data.get("date")))

    all_phoenix_log_files = []
    for i in range(1, 12 + 1):
        phoenix_log_path = rf"logs\original_logs\phoenixminer\{i:02d}"
        if not os.path.exists(phoenix_log_path):
            continue
        files = os.listdir(phoenix_log_path)
        all_phoenix_log_files += files

    share_dict_list = []
    next_payout_index = 0
    for log_file_path in all_phoenix_log_files:
        share_dict = dict(total=0, rejected=0, accepted=0)
        with open(log_file_path, "r") as log_file:
            log_file_text = log_file.read()

        share_dict["total"] += 1
        share_dict["accepted"] += 1

        # 3 states: 1. sammeln für einen payout, 2. wechsel auf nächsten payout, 3. ignorieren für ausstehenden payout
        # check if date is before first payout
        # check if payout occured inside log
        # check if date is after last payout


