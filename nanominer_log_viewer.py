from datetime import datetime
import logging
from pathlib import Path
from classes import ShareClass, LogEvalClass
from colorama import Fore

def _get_line_datetime(line: str) -> datetime:
    # old: 2021-02-27 17:24:24: <info>.....
    # new 2021-Apr-30 20:58:17:
    line = line[:20].removesuffix(":")
    try:
        return datetime.strptime(line.split(": ")[0], '%Y-%m-%d %H:%M:%S')
    except ValueError:
        try:
            return datetime.strptime(line.split(": ")[0], '%Y-%b-%d %H:%M:%S')
        except ValueError:
            return datetime.min


def _get_first_dateline(lines: list[str]) -> datetime:
    for line in lines:
        line_date = _get_line_datetime(line)
        if line_date != datetime.min:
            return line_date


def _get_last_dateline(lines: list[str]) -> datetime:
    for line in reversed(lines):
        line_date = _get_line_datetime(line)
        if line_date != datetime.min:
            return line_date


def _get_share_dict_from_line(line) -> ShareClass:
    line_split = line.split("Total shares: ")[1]
    line_split = line_split.split("Rejected: ")
    total_shares = int(line_split[0])
    rejected_shares = int(line_split[1].split(",")[0])
    shares = ShareClass(accepted=(total_shares - rejected_shares), rejected=rejected_shares)
    del line_split, total_shares, rejected_shares
    return shares


def _get_shares_from_log_inside_payout_window(lines: list[str]) -> ShareClass:
    for line in reversed(lines):
        if line.find("Total shares: ") != -1:
            return _get_share_dict_from_line(line)
    del line, lines


def _get_share_stats_from_log_before_payout_part(lines: list[str], next_payout_timestamp: datetime) -> ShareClass:
    for i in reversed(range(0, len(lines))):
        line = lines[i]
        if line.find("Total shares: ") != -1:
            line_timestamp = _get_line_datetime(line)
            if line_timestamp < next_payout_timestamp:
                return _get_share_dict_from_line(line)


def analyse_nano_log(log_file_path: Path, payout_dates: list[datetime]) -> [list[LogEvalClass], bool]:
    print(log_file_path)
    with open(log_file_path, "r") as log_file:
        log_file_text = log_file.read()
    del log_file

    if log_file_text.find("shares: ") == -1:
        print(f"{Fore.RED}Log was empty{Fore.RESET}")
        return []

    lines = log_file_text.splitlines(keepends=False)
    del log_file_text
    log_start_time = _get_first_dateline(lines)
    log_end_time = _get_last_dateline(lines)

    continueing_log = False
    # prüfe ob dies ein fortführender log ist, wenn ja setze

    for payout in payout_dates:
        if log_start_time < payout:
            if log_end_time < payout:
                # print("Log fully inside payout window")
                log_eval = LogEvalClass(payout_worked_for=payout,
                                        shares=_get_shares_from_log_inside_payout_window(lines),
                                        runtime=log_end_time - log_start_time)
                print(log_eval)
                return [[log_eval], continueing_log]
            else:
                # print("Payout inside this log")
                first = _get_share_stats_from_log_before_payout_part(lines, payout)
                first_eval = LogEvalClass(payout_worked_for=payout,
                                          shares=first,
                                          runtime=payout - log_start_time)
                print(first_eval)

                next_payout = payout_dates[payout_dates.index(payout) + 1]
                second = _get_shares_from_log_inside_payout_window(lines)
                second = second - first

                second_eval = LogEvalClass(payout_worked_for=next_payout,
                                           shares=second,
                                           runtime=log_end_time - payout)
                print(second_eval)
                return [[first_eval, second_eval], continueing_log]

        else:
            pass
            # print("go to next payout date")

    logging.error("Should not reach end here!")
    return []
