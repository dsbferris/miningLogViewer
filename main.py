import os

nanominerlogspath = r"C:\Users\Ferris\Desktop\Mining Logs\nanominer\Bis April 2021"
nanominerBigLogBeforeAprilPath = r"C:\Users\Ferris\Desktop\Mining Logs\nanominer_biglog_before_April.log"
nanomineSubLogPath = r"C:\Users\Ferris\Desktop\Mining Logs\nanominer_new_splitted_before_april"

# der anfang der zeile mit diesem inhalt stellt den anfang eines mining logs dar
nanominer_log_seperator = "                                    _                 "


def getNanoMinerBigLog():
    bigLog = ""
    logfiles = os.listdir(nanominerlogspath)
    count = 0
    for file in logfiles:
        count += 1
        singleLogFilePath = os.path.join(nanominerlogspath, file)
        with open(singleLogFilePath, "r") as logFile:
            bigLog += logFile.read()

    print(f"Found {count} logfiles\n")
    return bigLog


def writeBigLogToFile(text: str):
    with open(nanominerBigLogBeforeAprilPath, "w") as bigLogFile:
        bigLogFile.write(text)


def readBigLogFile():
    with open(nanominerBigLogBeforeAprilPath, "r") as bigLogFile:
        return bigLogFile.read()


def get_index_of_new_line_before_given_index(text: str, index: int):
    for i in reversed(range(index - 100,
                            index)):  # seperator index liegt bei ~22. Damit sollte bis 100 Zeichen zuvor sich die newline finden lassen
        if i >= 0:
            if text[i] == '\n':
                return i

    return -1


def split_big_log_into_pieces(bigLog: str):
    count = 0
    first_separator_index = bigLog.find(nanominer_log_seperator)  # den aller ersten separator ignorieren
    recent_split_index = -1
    recent_separator_index = first_separator_index

    # ohne +1 würde der vorherige wiederverwendet werden
    next_separator_index = bigLog.find(nanominer_log_seperator, recent_separator_index + 1)
    while next_separator_index != -1:
        next_split_index = get_index_of_new_line_before_given_index(bigLog, next_separator_index)
        assert next_split_index != -1
        sub_log = bigLog[recent_split_index + 1:next_split_index]  # to prevent an empty line at new sublog
        sub_log_path = os.path.join(nanomineSubLogPath, f"sublog_{count}_{sub_log[:20].replace(':', '.').strip()}.log")
        with open(sub_log_path, "w") as subLogFile:
            subLogFile.write(sub_log)
        print(f"Created {sub_log_path}\n")

        recent_split_index = next_split_index
        recent_separator_index = next_separator_index
        next_separator_index = bigLog.find(nanominer_log_seperator, recent_separator_index + 1)
        count += 1

    # handle last log
    sub_log = bigLog[recent_split_index:]
    sub_log_path = os.path.join(nanomineSubLogPath, f"sublog_{count}_{sub_log[:20].replace(':', '.').strip()}.log")
    with open(sub_log_path, "w") as subLogFile:
        subLogFile.write(sub_log)

    print(f"Created {sub_log_path}")


def check_sublogs_are_valid():
    logfiles = os.listdir(nanominerlogspath)
    count = 0
    for file in logfiles:
        count += 1
        singleLogFilePath = os.path.join(nanomineSubLogPath, file)
        with open(singleLogFilePath, "r") as logFile:
            logFileText = logFile.read()

        accepted, rejected = 0
        for line in logFileText.splitlines(keepends=False):
            if line.find("Total shares:") != -1:
                #  2021-02-13 14:12:14: [Statistics] Ethereum - Total speed: 56.586 MH/s, Total shares: 0 Rejected: 0, Time: 00:32
                total_split = line.split("Total shares: ")
                total_shares = int(total_split[1][0])
                rejected_split = total_split[1].split("Rejected: ")
                rejected_shares = int(rejected_split[1][0])


    print(f"Found {count} logfiles\n")


# bigLog = getNanoMinerBigLog()
# writeBigLogToFile(bigLog)
bigLog = readBigLogFile()
split_big_log_into_pieces(bigLog)
