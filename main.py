import old_log_viewer as olv

import os


def find_possible_errors(month):
    log_path = rf"C:\Users\Ferris\PycharmProjects\pythonProject\logs\original_logs\nanominer\{month:02d}"
    wallet = "RTX 3070"
    files = os.listdir(log_path)
    count = 0
    for file in files:
        file_path = os.path.join(log_path, file)
        with open(file_path, "r") as log_file:
            log_text = log_file.read()
        count = log_text.count(wallet)
        if count > 1:
            print(f"Double occurrence in {file_path}")


for i in range(2, 5+1):
    olv.run(i)
    find_possible_errors(i)