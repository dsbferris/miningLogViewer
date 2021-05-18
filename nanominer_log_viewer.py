import os


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
    split_separator = "RTX 3070"
    parts = big_log.split(split_separator)[1:]
    total_secs = 0
    for part in parts:

        index = part.rfind("Time:")

        try:
            assert index != -1
        except AssertionError:
            print(f"Error in part:\n{part}")

        new_line = part.find("\n", index)
        time = part[index:new_line]  # e.g. for time: (Time: )04:02:01(\n)
        total_secs += read_seconds_from_line(time)

    return total_secs


def get_total_seconds(log_path):
    big_log = read_all_logs_and_return_big_log(log_path)
    total_seconds = read_total_seconds_from_big_log(big_log)
    return total_seconds
