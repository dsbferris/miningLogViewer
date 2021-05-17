import os
import datetime
import sys


def create_big_log(log_path: str):
    with open("big_log.txt", "w") as text_file:
        text_file.write(read_all_logs(log_path))


def read_all_logs(log_path: str):
    big_log = ""
    files = os.listdir(log_path)
    count = 0
    for file in files:
        if file.endswith(".log"):
            count += 1
            filepath = os.path.join(log_path, file)
            # print(filepath)
            with open(filepath, "r") as log_file:
                big_log += log_file.read()
    print(f"{count} logs")
    return big_log


def read_times_from_big_log(wattage: int, price: float):
    with open("big_log.txt", "r") as big_log_file:
        lines = big_log_file.read()
        return read_times(lines, wattage, price)


def read_times(big_log, wattage: int, price: float):
    # split_separator = "wallet"
    split_separator = "RTX 3070"
    parts = big_log.split(split_separator)[1:]
    total_secs = 0
    for part in parts:

        index = part.rfind("Time:")
        if index == -1:
            continue

        new_line = part.find("\n", index)
        time = part[index: new_line]

        if time.endswith("s"):
            time_split = time.split(" ")
            for ts in time_split:
                if ts.find("Time:") != -1:
                    continue
                elif ts.find("d") != -1:
                    days = int(ts.replace("d", ""))
                    total_secs += days * 24 * 60 * 60
                elif ts.find("h") != -1:
                    hours = int(ts.replace("h", ""))
                    total_secs += hours * 60 * 60
                elif ts.find("m") != -1:
                    minutes = int(ts.replace("m", ""))
                    total_secs += minutes * 60
                elif ts.find("s") != -1:
                    seconds = int(ts.replace("s", ""))
                    total_secs += seconds

        else:
            time_solo = time.split(" ")[-1:][0]
            time_parts = [int(s) for s in time_solo.split(':')]
            if len(time_parts) == 3:
                total_secs += time_parts[0] * 3600 + time_parts[1] * 60 + time_parts[2]
            elif len(time_parts) == 2:
                total_secs += time_parts[0] * 60 + time_parts[1]

    total_hours = total_secs / 3600
    kwh = total_hours * (wattage / 1000)
    total_secs, sec = divmod(total_secs, 60)
    hr, min = divmod(total_secs, 60)
    days, hr = divmod(hr, 24)
    print("%d Days, %dh:%02dm:%02ds" % (days, hr, min, sec))

    kwh = total_hours * (wattage / 1000)
    print("\033[1m At %dW & %.4f€/KWh: \033[4m%.4fKWh\033[0m, \033[4m%.4f€\033[0m\033[0m"
          % (wattage, price, kwh, kwh * price))


def main(log_path: str, wattage: int, price: float):
    create_big_log(log_path)
    read_times_from_big_log(wattage, price)


def run(month):
    print(f"Month: {month}")
    wattage = 170
    if month >= 4:
        cost = 0.298
    else:
        cost = 0.2735
    log_path = rf"C:\Users\Ferris\PycharmProjects\pythonProject\logs\original_logs\nanominer\{month:02d}"

    big_log = read_all_logs(log_path)
    read_times(big_log, wattage, cost)
    print("\n")

