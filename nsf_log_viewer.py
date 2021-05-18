import os


def clean_log(log_file_path: str):
    clean_log_text = ""
    with open(log_file_path, "r") as log_file:
        clean_log_text = log_file.read()

    clean_log_text = clean_log_text.replace("[37m", "")
    clean_log_text = clean_log_text.replace("[97m", "")
    clean_log_text = clean_log_text.replace("[0m", "")
    clean_log_text = clean_log_text.replace("[32m", "")
    clean_log_text = clean_log_text.replace("[36m", "")
    clean_log_text = clean_log_text.replace("[93m", "")
    clean_log_text = clean_log_text.replace("[1;97m", "")
    clean_log_text = clean_log_text.replace("[91m", "")
    clean_log_text = clean_log_text.replace("[1;36m", "")
    clean_log_text = clean_log_text.replace("[92m", "")
    return clean_log_text


def write_clean_log(file_name_before: str, log_path: str, clean_log_text: str):
    new_path = file_name_before.removesuffix(".log") + "_clean.log"
    new_path = os.path.join(log_path, new_path)
    with open(new_path, "w") as clean_log_file:
        clean_log_file.write(clean_log_text)


def create_clean_logs(log_path):
    files = os.listdir(log_path)
    for file in files:
        if file.endswith(".log") and not file.endswith("_clean.log"):
            log_file_path = os.path.join(log_path, file)
            clean_log_text = clean_log(log_file_path)
            write_clean_log(file, log_path, clean_log_text)







