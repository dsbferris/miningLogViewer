import csv
import datetime as dt
import os
import shutil
from os import path

import numpy as np
import matplotlib.dates as md
import matplotlib.pyplot as plt
import pandas as pd

# der anfang der zeile mit diesem inhalt stellt den anfang eines mining logs dar
nanominer_log_seperator = "                                    _                 "


def generate_big_log(original_log_path):
    bigLog = ""
    logfiles = os.listdir(original_log_path)
    count = 0
    for file in logfiles:
        count += 1
        singleLogFilePath = os.path.join(original_log_path, file)
        with open(singleLogFilePath, "r") as logFile:
            bigLog += logFile.read()

    print(f"Found {count} logfiles\n")
    return bigLog


def write_big_log_to_file(text: str, big_log_path: str):
    with open(big_log_path, "w") as bigLogFile:
        bigLogFile.write(text)


def read_big_log_file(big_log_path: str):
    with open(big_log_path, "r") as bigLogFile:
        return bigLogFile.read()


def get_index_of_new_line_before_given_index(text: str, index: int):
    # separator index liegt bei ~22. Damit sollte bis 50 Zeichen zuvor sich die newline finden lassen
    for i in reversed(range(index - 50, index)):
        if i >= 0:
            if text[i] == '\n':
                return i

    return -1


def get_sub_log_file_path(sub_log_text, count, sub_log_path):
    timestamp = sub_log_text[:20].replace(':', '.').strip().removesuffix(".")
    return os.path.join(sub_log_path, f"{timestamp}_sublog_{count}.log")


def split_big_log_into_sub_logs(big_log: str, sub_log_path: str):
    # Delete all existing sublogs and recreate empty dir
    if path.exists(sub_log_path):
        shutil.rmtree(sub_log_path)
    os.mkdir(sub_log_path)

    count = 0
    first_separator_index = big_log.find(nanominer_log_seperator)  # den aller ersten separator ignorieren
    recent_split_index = -1
    recent_separator_index = first_separator_index

    # ohne +1 würde der vorherige wiederverwendet werden
    next_separator_index = big_log.find(nanominer_log_seperator, recent_separator_index + 1)
    while next_separator_index != -1:
        next_split_index = get_index_of_new_line_before_given_index(big_log, next_separator_index)
        assert next_split_index != -1
        sub_log = big_log[recent_split_index + 1:next_split_index]  # to prevent an empty line at new sub_log
        sub_log_file_path = get_sub_log_file_path(sub_log, count, sub_log_path)
        with open(sub_log_file_path, "w") as sub_log_file:
            sub_log_file.write(sub_log)
        print(f"Created {sub_log_file_path}")

        recent_split_index = next_split_index
        recent_separator_index = next_separator_index
        next_separator_index = big_log.find(nanominer_log_seperator, recent_separator_index + 1)
        count += 1

    # handle last log
    sub_log = big_log[recent_split_index:]
    sub_log_file_path = get_sub_log_file_path(sub_log, count, sub_log_path)
    with open(sub_log_file_path, "w") as sub_log_file:
        sub_log_file.write(sub_log)

    print(f"Created {sub_log_file_path}")


def check_single_sub_log_valid(sub_log_text: str, file: str):
    total = 0
    line_count = 0
    for line in sub_log_text.splitlines(keepends=False):
        line_count += 1
        if line.find("Total shares:") != -1:
            #  2021-02-13 14:12:14: [Statistics] Ethereum - Total speed: 56.586 MH/s, Total shares: 0 Rejected: 0, Time: 00:32
            total_split = line.split("Total shares: ")[1].split(" Rejected:")
            total_shares = int(total_split[0])
            try:
                assert total <= total_shares
                total = total_shares
            except AssertionError:
                print(f"Violation found in file {file} at line {line_count}")
                return 1

    return 0


def check_sub_logs_are_valid(sub_log_path: str):
    sub_log_path_files = os.listdir(sub_log_path)
    count = 0
    violation_count = 0
    for file in sub_log_path_files:
        count += 1
        sub_log_file_path = os.path.join(sub_log_path, file)
        with open(sub_log_file_path, "r") as logFile:
            log_file_text = logFile.read()

        violation_count += check_single_sub_log_valid(log_file_text, file)
    print(f"{count} sublogs found!")
    print(f"{violation_count} violations found!")


def debloat_sub_logs(sub_log_path: str):
    sub_log_path_files = os.listdir(sub_log_path)
    debloated_lines = 0
    for file in sub_log_path_files:
        sub_log_file_path = os.path.join(sub_log_path, file)
        with open(sub_log_file_path, "r") as f:
            lines = f.readlines()
        with open(sub_log_file_path, "w") as f:
            for line in lines:
                if line.strip("\n").find("New job from") == -1:
                    f.write(line)
                else:
                    debloated_lines += 1
    print(f"Debloated {debloated_lines} lines")


def generate_sub_logs_for_nanominer_before_april():
    nanominer_log_path_before_april = r"logs\original_logs\nanominer\Bis April 2021"
    nanominer_big_log_path_before_april = r"logs\refactored_logs\nanominer_big_log_before_april.log"
    nanominer_sub_log_path_before_april = r"logs\refactored_logs\nanominer_sub_logs_before_april"

    big_log = generate_big_log(nanominer_log_path_before_april)
    write_big_log_to_file(big_log, nanominer_big_log_path_before_april)
    big_log = read_big_log_file(nanominer_big_log_path_before_april)

    split_big_log_into_sub_logs(big_log, nanominer_sub_log_path_before_april)
    check_sub_logs_are_valid(nanominer_sub_log_path_before_april)
    debloat_sub_logs(nanominer_sub_log_path_before_april)


def generate_sub_logs_for_nanominer_after_april():
    nanominer_log_path_after_april = r"logs\original_logs\nanominer\Nach April 2021"
    nanominer_big_log_after_april_path = r"logs\refactored_logs\nanominer_big_log_after_april.log"
    nanominer_sub_log_path_after_april = r"logs\refactored_logs\nanominer_sub_logs_after_april"

    big_log = generate_big_log(nanominer_log_path_after_april)
    write_big_log_to_file(big_log, nanominer_big_log_after_april_path)
    big_log = read_big_log_file(nanominer_big_log_after_april_path)

    split_big_log_into_sub_logs(big_log, nanominer_sub_log_path_after_april)
    check_sub_logs_are_valid(nanominer_sub_log_path_after_april)
    debloat_sub_logs(nanominer_sub_log_path_after_april)


def get_datetime_from_string(timestring: str):
    datesplit = timestring.split('-')
    year = int(datesplit[0])
    #month can be numeric or string (e.g. "Apr")
    if datesplit[1].isdecimal():
        month = int(datesplit[1])
    else:
        if datesplit[1] == "Mar":
            month = 3
        elif datesplit[1] == "Apr":
            month = 4
        elif datesplit[1] == "May":
            month = 5
        else:
            print(f"No month found for '{datesplit[1]}'")
            raise NotImplementedError
    day_time_split = datesplit[2].split(' ')
    day = int(day_time_split[0])
    time_split = day_time_split[1].split(':')
    hours = int(time_split[0])
    minutes = int(time_split[1])
    sec = int(time_split[2])

    return dt.datetime(year=year, month=month, day=day, hour=hours, minute=minutes, second=sec)


def get_data_from_logs(sub_log_path):
    data_set = []
    sub_log_path_files = os.listdir(sub_log_path)
    for file in sub_log_path_files:
        sub_log_file_path = os.path.join(sub_log_path, file)
        with open(sub_log_file_path, "r") as f:
            lines = f.readlines()
        for line in lines:
            line = line.strip()
            if line.find("Ethereum - Total speed:") != -1: # So we got a valid line
                timestring = line[:19]
                timestamp = get_datetime_from_string(timestring)
                mhs = float(line.split('Total speed: ')[1].split(' ')[0])
                total_shares = int(line.split("Total shares: ")[1].split(' ')[0])
                rejected_shares = int(line.split("Rejected: ")[1].split(',')[0])
                runtime = line.split("Time: ")[1]
                data_set.append([timestamp, mhs, total_shares, rejected_shares, runtime])

    return data_set

def save_data_to_file(data: [], filename: str):
    header = ["Timestamp,Hashrate,TotalShares,RejectShares,Runtime"]
    with open(filename, "w") as data_file:
        writer = csv.writer(data_file)
        writer.writerow(header)
        writer.writerows(data)
    # header = "Timestamp, Hashrate, TotalShares, RejectedShares, Runtime"
    # np.savez(filename, data, header=header)


def read_data_from_file(filepath: str):

    return np.load(filepath, allow_pickle=True)


def restructure_data(data):
    timestamps = []
    hashrates = []
    totalshares = []
    rejectshares = []
    for t in log_data:
        timestamps.append(t[0])
        hashrates.append(t[1])
        totalshares.append(t[2])
        rejectshares.append(t[3])
    datenums = md.date2num(timestamps)
    restructured_log_data = [datenums, hashrates, totalshares, rejectshares]
    return restructured_log_data

def start():
    generate_sub_logs_for_nanominer_before_april()
    generate_sub_logs_for_nanominer_after_april()

data_save_filepath = "data.csv"
# log_data = get_data_from_logs(r"logs\refactored_logs\nanominer_sub_logs_before_april")

# save_data_to_file(log_data, data_save_filepath)

log_data = pd.read_csv(data_save_filepath)

# save_data_to_file(restructure_data(log_data), data_save_filepath)

# log_data = read_data_from_file(data_save_filepath)

timestamps = md.num2date(log_data[0])


# Basic stacked area chart.
plt.xticks(rotation=25)
plt.plot(timestamps, log_data[2])
plt.show()