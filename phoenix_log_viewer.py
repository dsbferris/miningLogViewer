from pathlib import Path
from datetime import datetime
import logging
from classes import ShareClass, LogEvalClass


def _get_line_datetime(line: str) -> datetime:
    try:
        return datetime.strptime(line.split(": ")[0], '%Y.%m.%d:%H:%M:%S.%f')
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
    line_split = line.split("shares: ")[1].split(",")[0].split("/")
    # Accepted, Rejected + incorrect
    return ShareClass(accepted=int(line_split[0]), rejected=(int(line_split[1]) + int(line_split[2])))


def _get_shares_from_log_inside_payout_window(lines: list[str]) -> ShareClass:
    for line in reversed(lines):
        if line.find("shares: ") != -1:
            return _get_share_dict_from_line(line)
    del line, lines


def _get_share_stats_from_log_before_payout_part(lines: list[str], next_payout_timestamp: datetime) -> ShareClass:
    for i in reversed(range(0, len(lines))):
        line = lines[i]
        if line.find("shares: ") != -1:
            line_timestamp = _get_line_datetime(line)
            if line_timestamp < next_payout_timestamp:
                return _get_share_dict_from_line(line)


#
# def _phoenix_total_shares(payout_dates: list[datetime], log_files: list[pathlib.Path]):
#     payout_dates.append(datetime.max)  # To check shares for outstanding payout
#
#     share_dict_list = []
#     share_dict = dict(accepted=0, rejected=0, incorrect=0)
#     next_payout_index = 0
#     for i in range(0, len(log_files)):
#         log_file_path = log_files[i]
#
#         with open(log_file_path, "r") as log_file:
#             log_file_text = log_file.read()
#         del log_file
#         # check if log is valid at all
#         if log_file_text.find("shares: ") == -1:
#             print("Skipped empty log:")
#             print(log_file_path)
#             print("")
#             continue
#
#         lines = log_file_text.splitlines(keepends=False)
#         log_start_time = _get_line_datetime(lines[0])
#         log_end_time = _get_line_datetime(lines[-1])
#
#         if i == 0:
#             while log_end_time > payout_dates[next_payout_index]:
#                 next_payout_index += 1
#                 share_dict_list.append(dict(accepted=0, rejected=0, incorrect=0))
#
#         if log_start_time < payout_dates[next_payout_index]:
#             if log_end_time < payout_dates[next_payout_index]:
#                 print("Log fully inside payout window")
#                 print(log_file_path)
#                 log_dict = get_share_stats_from_log_inside_payout_window(lines)
#                 print(log_dict)
#                 share_dict = add_dicts(share_dict, log_dict)
#                 del log_dict
#                 print("")
#
#             else:
#                 print("Payout inside this log")
#                 print(log_file_path)
#                 first_part = get_share_stats_from_log_before_payout_part(lines, payout_dates[next_payout_index])
#                 print(first_part)
#                 share_dict = add_dicts(share_dict, first_part)
#                 share_dict_list.append(share_dict)
#
#                 next_payout_index += 1
#
#                 second_part = get_share_stats_from_log_inside_payout_window(lines)
#                 for key in first_part.keys():
#                     second_part[key] -= first_part[key]
#                 share_dict = second_part
#                 print(second_part)
#                 print("")
#                 del first_part, second_part, key
#         else:
#             print("payout occured between logs")
#             next_payout_index += 1
#             share_dict_list.append(share_dict)
#     share_dict_list.append(share_dict)
#     del share_dict, i, next_payout_index, log_file_text, log_file_path, log_start_time, log_end_time, lines, log_files
#     if len(payout_dates) != len(share_dict_list):
#         raise Exception("not fitting payout dates and share_dict_list length!")
#
#     for i in range(0, len(share_dict_list)):
#         print(f"{payout_dates[i]}: {share_dict_list[i]}")

def analyse_phoenix_log(log_file_path: Path, payout_dates: list[datetime]) -> list[LogEvalClass]:
    print(log_file_path)
    with open(log_file_path, "r") as log_file:
        log_file_text = log_file.read()
    del log_file

    if log_file_text.find("shares: ") == -1:
        return []

    lines = log_file_text.splitlines(keepends=False)
    del log_file_text
    log_start_time = _get_first_dateline(lines)
    log_end_time = _get_last_dateline(lines)

    for payout in payout_dates:
        if log_start_time < payout:
            # print("log fits payout date")
            if log_end_time < payout:
                # print("Log fully inside payout window")
                log_eval = LogEvalClass(payout_worked_for=payout,
                                        shares=_get_shares_from_log_inside_payout_window(lines),
                                        runtime=log_end_time - log_start_time)
                print(log_eval)
                return [log_eval]
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

                second_eval_v2 = LogEvalClass(payout_worked_for=next_payout,
                                              shares=second,
                                              runtime=log_end_time - payout)
                print(second_eval_v2)
                return [first_eval, second_eval_v2]

        else:
            pass
            # print("go to next payout date")

    logging.error("Should not reach end here!")
    return []
