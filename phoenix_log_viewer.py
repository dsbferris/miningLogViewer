import os
import datetime
import requests

#region Runtime


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

#endregion

#region Share counting


def get_nanopool_payout_dates() -> list[datetime.datetime]:
    response = requests.get("https://api.nanopool.org/v1/eth/payments/0x88276b6528b600e290f0c4598162aa31e0d30639")
    payout_dates = []
    if response.ok:
        json = response.json()
        payout_data = json.get("data")
        for data in reversed(payout_data):
            payout_dates.append(datetime.datetime.fromtimestamp(data.get("date")))
        del json, payout_data, response, data
    return payout_dates


def get_list_of_all_phoenix_log_file_paths() -> list[str]:
    all_phoenix_log_files = []
    for i in range(1, 12 + 1):
        phoenix_log_path = rf"logs\original_logs\phoenixminer\{i:02d}"
        if not os.path.exists(phoenix_log_path):
            continue
        files = os.listdir(phoenix_log_path)
        for file in files:
            all_phoenix_log_files.append(os.path.join(phoenix_log_path, file))
    del phoenix_log_path, file, files, i
    return all_phoenix_log_files


def get_share_stats_from_log_inside_payout_window(lines: list[str]) -> dict:
    share_dict = dict(total=0, rejected=0, incorrect=0)
    for line in reversed(lines):
        if line.find("shares: ") != -1:
            shares = line.split("shares: ")[1].split(",")[0].split("/")
            # print(shares)
            share_dict['total'] = shares[0]
            share_dict['rejected'] = shares[1]
            share_dict['incorrect'] = shares[2]
            break
    del line, lines
    print(share_dict)
    return share_dict


def phoenix_total_shares():
    payout_dates = get_nanopool_payout_dates()
    all_phoenix_log_files = get_list_of_all_phoenix_log_file_paths()


    share_dict_list = []
    share_dict = dict(total=0, rejected=0, incorrect=0)
    next_payout_index = 0
    for i in range(0, len(all_phoenix_log_files)):
        log_file_path = all_phoenix_log_files[i]

        with open(log_file_path, "r") as log_file:
            log_file_text = log_file.read()
        del log_file

        lines = log_file_text.splitlines(keepends=False)
        log_start_time = datetime.datetime.strptime(lines[0].split(": ")[0], '%Y.%m.%d:%H:%M:%S.%f')
        log_end_time = datetime.datetime.strptime(lines[-1].split(": ")[0], '%Y.%m.%d:%H:%M:%S.%f')
        if log_start_time < payout_dates[next_payout_index]:
            if log_end_time < payout_dates[next_payout_index]:
                print("All in payout")
                for line in reversed(lines):
                    if line.find("shares: ") != -1:
                        shares = line.split("shares: ")[1].split(",")[0].split("/")
                        print(shares)
                        share_dict['total'] = shares[0]
                        share_dict['rejected'] = shares[1]
                        share_dict['incorrect'] = shares[2]
                        break

            else:
                print("Payout occured in log")
        else:
            print("payout occured between logs")
            next_payout_index += 1
            if next_payout_index >= len(payout_dates):
                print("Alle payout daten gesammelt. Kein grund weiter logs zu durchsuchen")
                break

        # datetime.datetime.strptime(first_line_time, '%Y.%m.%d:%H:%M:%S.%f')
        # 2021.05.10:20:30:45.561

        # 3 states: 1. sammeln für einen payout, 2. wechsel auf nächsten payout, 3. ignorieren für ausstehenden payout
        # check if date is before first payout
        # check if payout occured inside log
        # check if date is after last payout


#endregion