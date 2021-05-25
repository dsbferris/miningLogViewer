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
