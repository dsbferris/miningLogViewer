import os
import datetime
import pathlib

import requests
import phoenix_log_viewer as plv
from pathlib import Path

# region Runtime Analysis


# Writes big_log into big_log_path
def write_big_log_to_file(big_log_path: str, big_log_text: str):
    with open(big_log_path, "w") as text_file:
        text_file.write(big_log_text)


# Reads big_log from file
def read_big_log_from_file(big_log_path: str):
    with open(big_log_path, "r") as big_log_file:
        big_log = big_log_file.read()
    return big_log


# Appends all .log file into one big_log and returns it
def read_all_logs_and_return_big_log(log_path: str):
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


# Reads normal log and looks up if a separator exists more than once in a file
def find_possible_errors(log_path: str, separator: str):
    files = os.listdir(log_path)
    for file in files:
        file_path = os.path.join(log_path, file)
        with open(file_path, "r") as log_file:
            log_text = log_file.read()
        count = log_text.count(separator)
        if count > 1:
            print(f"Double occurrence of split separator in {file_path}")


# Returns seconds from printed time in log (e.g. 04:20:01, 1d 2h 3m 4s)
def read_seconds_from_line(time: str):
    total_seconds = 0
    if time.endswith("s"):
        time_split = time.split(" ")
        for ts in time_split:
            if ts.find("Time:") != -1:
                continue
            elif ts.find("d") != -1:
                days = int(ts.replace("d", ""))
                total_seconds += days * 24 * 60 * 60
            elif ts.find("h") != -1:
                hours = int(ts.replace("h", ""))
                total_seconds += hours * 60 * 60
            elif ts.find("m") != -1:
                minutes = int(ts.replace("m", ""))
                total_seconds += minutes * 60
            elif ts.find("s") != -1:
                seconds = int(ts.replace("s", ""))
                total_seconds += seconds

    else:
        time_solo = time.split(" ")[-1:][0]
        time_parts = [int(s) for s in time_solo.split(':')]
        if len(time_parts) == 3:
            total_seconds += time_parts[0] * 3600 + time_parts[1] * 60 + time_parts[2]
        elif len(time_parts) == 2:
            total_seconds += time_parts[0] * 60 + time_parts[1]
    return total_seconds


# Splits big_log into pieces and reads the last written time and sums up into seconds
def read_total_seconds_from_big_log(big_log: str):
    # split_separator = "wallet"
    split_separator = "8192 MB available"
    parts = big_log.split(split_separator)[1:]
    total_secs = 0
    part_index = 0
    for part in parts:
        part_index += 1
        index = part.rfind("Time:")
        if index == -1:
            print(f"No time found in :\n{parts[part_index]}")
            continue

        new_line = part.find("\n", index)
        time = part[index:new_line]  # e.g. for time: (Time: )04:02:01(\n)
        total_secs += read_seconds_from_line(time)

    return total_secs


def get_total_seconds(log_path):
    big_log = read_all_logs_and_return_big_log(log_path)
    total_seconds = read_total_seconds_from_big_log(big_log)
    return total_seconds


#endregion


def get_line_datetime(line: str) -> datetime.datetime:
    # old: 2021-02-27 17:24:24: <info>.....
    # new 2021-Apr-30 20:58:17:
    line = line[:20].removesuffix(":")
    try:
        return datetime.datetime.strptime(line.split(": ")[0], '%Y-%m-%d %H:%M:%S')
    except ValueError:
        try:
            return datetime.datetime.strptime(line.split(": ")[0], '%Y-%b-%d %H:%M:%S')
        except ValueError:
            return datetime.datetime.min


levin_rootpath = "./logs/original_logs/levin_nanominer_logs/levin_new"
ferris_rootpath = "./logs/original_logs/nanominer"


def get_list_of_all_nanominer_log_file_paths(rootpath: str):
    return list(Path(rootpath).rglob("*.*"))


def get_share_dict_from_line(line) -> dict:
    share_dict = dict(total=0, rejected=0, accepted=0)
    line_split = line.split("Total shares: ")[1]

    total_shares = int(line_split.split(" ")[0])
    rejected_shares = int(line_split.split("Rejected: ")[0])

    share_dict['total'] = total_shares
    share_dict['rejected'] = rejected_shares
    share_dict['accepted'] = total_shares - rejected_shares
    del line_split, total_shares, rejected_shares
    return share_dict


def get_share_stats_from_log_inside_payout_window(lines: list[str]) -> dict:
    for line in reversed(lines):
        if line.find("Total shares: ") != -1:
            return get_share_dict_from_line(line)
    del line, lines


dates = plv.get_nanopool_payout_dates()
ddict = plv.add_dicts(dict(), dict())
