import os
import pathlib
from datetime import datetime, timedelta
import requests


# region Runtime


def _get_log_runtime(log_file_path):
    with open(log_file_path, "r") as log_file:
        log_file_text = log_file.read()
    split = log_file_text.splitlines(False)
    first_line = split[0]
    last_line = split[-1]
    first_line_time = first_line.split(" ")[0].removesuffix(":")
    last_line_time = last_line.split(" ")[0].removesuffix(":")
    first_timestamp = datetime.strptime(first_line_time, '%Y.%m.%d:%H:%M:%S.%f')
    last_timestamp = datetime.strptime(last_line_time, '%Y.%m.%d:%H:%M:%S.%f')
    delta = last_timestamp - first_timestamp
    return delta


def _get_all_logs_total_seconds(log_path) -> float:
    delta_sum = timedelta(0)
    files = os.listdir(log_path)
    for file in files:
        file_path = os.path.join(log_path, file)
        delta_sum += _get_log_runtime(file_path)
    return delta_sum.total_seconds()


# endregion


# region Share counting


def _get_line_datetime(line: str) -> datetime:
    try:
        return datetime.strptime(line.split(": ")[0], '%Y.%m.%d:%H:%M:%S.%f')
    except ValueError:
        return datetime.min


def add_dicts(a: dict, b: dict) -> dict:
    if set(a.keys()) != set(b.keys()):
        raise Exception("dicts dont fit keys!!!s")
    else:
        for key in a.keys():
            if not isinstance(a[key], int):
                raise Exception("a is not int!")
            elif not isinstance(b[key], int):
                raise Exception("b is not int!")
            else:
                a[key] += b[key]

        return a


def get_share_dict_from_line(line) -> dict:
    share_dict = dict(accepted=0, rejected=0, incorrect=0)
    shares = line.split("shares: ")[1].split(",")[0].split("/")
    # print(shares)
    share_dict['accepted'] = int(shares[0])
    share_dict['rejected'] = int(shares[1])
    share_dict['incorrect'] = int(shares[2])
    return share_dict


def get_share_stats_from_log_inside_payout_window(lines: list[str]) -> dict:
    for line in reversed(lines):
        if line.find("shares: ") != -1:
            return get_share_dict_from_line(line)
    del line, lines


# this is still slow, maybe improve code here
def get_share_stats_from_log_before_payout_part(lines: list[str], next_payout_timestamp: datetime) -> dict:
    for line in reversed(lines):
        line_timestamp = _get_line_datetime(line)
        if line_timestamp == datetime.min:
            continue  # in case of a line like 'GPUs Power...' without timestamp
        if line_timestamp < next_payout_timestamp:
            if line.find("shares: ") != -1:
                return get_share_dict_from_line(line)


def phoenix_total_shares(payout_dates: list[datetime], log_files: list[pathlib.Path]):
    payout_dates.append(datetime.max)  # To check shares for outstanding payout

    share_dict_list = []
    share_dict = dict(accepted=0, rejected=0, incorrect=0)
    next_payout_index = 0
    for i in range(0, len(log_files)):
        log_file_path = log_files[i]

        with open(log_file_path, "r") as log_file:
            log_file_text = log_file.read()
        del log_file
        # check if log is valid at all
        if log_file_text.find("shares: ") == -1:
            print("Skipped empty log:")
            print(log_file_path)
            print("")
            continue

        lines = log_file_text.splitlines(keepends=False)
        log_start_time = _get_line_datetime(lines[0])
        log_end_time = _get_line_datetime(lines[-1])

        if i == 0:
            while log_end_time > payout_dates[next_payout_index]:
                next_payout_index += 1
                share_dict_list.append(dict(accepted=0, rejected=0, incorrect=0))

        if log_start_time < payout_dates[next_payout_index]:
            if log_end_time < payout_dates[next_payout_index]:
                print("Log fully inside payout window")
                print(log_file_path)
                log_dict = get_share_stats_from_log_inside_payout_window(lines)
                print(log_dict)
                share_dict = add_dicts(share_dict, log_dict)
                del log_dict
                print("")

            else:
                print("Payout inside this log")
                print(log_file_path)
                first_part = get_share_stats_from_log_before_payout_part(lines, payout_dates[next_payout_index])
                print(first_part)
                share_dict = add_dicts(share_dict, first_part)
                share_dict_list.append(share_dict)

                next_payout_index += 1

                second_part = get_share_stats_from_log_inside_payout_window(lines)
                for key in first_part.keys():
                    second_part[key] -= first_part[key]
                share_dict = second_part
                print(second_part)
                print("")
                del first_part, second_part, key
        else:
            print("payout occured between logs")
            next_payout_index += 1
            share_dict_list.append(share_dict)
    share_dict_list.append(share_dict)
    del share_dict, i, next_payout_index, log_file_text, log_file_path, log_start_time, log_end_time, lines, log_files
    if len(payout_dates) != len(share_dict_list):
        raise Exception("not fitting payout dates and share_dict_list length!")

    for i in range(0, len(share_dict_list)):
        print(f"{payout_dates[i]}: {share_dict_list[i]}")

# endregion
