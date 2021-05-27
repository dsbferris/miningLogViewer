import nanominer_log_viewer as nlv
import phoenix_log_viewer as plv
import os


# Prints out used KW/h and total cost in € for given values
def print_statistics(total_seconds: int, wattage: int, price: float):
    total_hours = total_seconds / 3600
    kwh = total_hours * (wattage / 1000)
    total_seconds, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(total_seconds, 60)
    days, hours = divmod(hours, 24)
    print("%d Days, %dh:%02dm:%02ds" % (days, hours, minutes, seconds))

    kwh = total_hours * (wattage / 1000)
    print("\033[1m At %dW & %.4f€/KWh: \033[4m%.4fKWh\033[0m, \033[4m%.4f€\033[0m\033[0m"
          % (wattage, price, kwh, kwh * price))



def get_nanominer():
    wattage = 170
    for i in range(2, 7):
        print(f"Month: {i}")
        if i >= 4:
            price = 0.298
        else:
            price = 0.2735

        nanominer_log_path = rf"C:\Users\Ferris\PycharmProjects\pythonProject\logs\original_logs\nanominer\{i:02d}"
        if os.path.exists(nanominer_log_path):
            nanominer_total_seconds = nlv.get_total_seconds(nanominer_log_path)
            print_statistics(nanominer_total_seconds, wattage, price)
            nlv.find_possible_errors(nanominer_log_path, "8192 MB available")
            print("\n")
        else:
            print(f"log_path does not exists: \n{nanominer_log_path}")


def get_nanominer_levin():
    wattage = 170
    price = 0.3
    nanominer_log_path = r"logs/original_logs/levin_nanominer_logs/logs"
    if os.path.exists(nanominer_log_path):
        nanominer_total_seconds = nlv.get_total_seconds(nanominer_log_path)
        print_statistics(nanominer_total_seconds, wattage, price)
        nlv.find_possible_errors(nanominer_log_path, "8192 MB available")
        print("\n")
    else:
        print(f"log_path does not exists: \n{nanominer_log_path}")


def get_phoenix_miner():

    wattage = 170
    for i in range(2, 7):
        print(f"Month: {i}")
        if i >= 4:
            price = 0.298
        else:
            price = 0.2735

        phoenix_log_path = rf"logs\original_logs\phoenixminer\{i:02d}"
        if os.path.exists(phoenix_log_path):
            phoenix_total_seconds = plv.get_all_logs_total_seconds(phoenix_log_path)
            print_statistics(phoenix_total_seconds, wattage, price)
            print("\n")
        else:
            print(f"log_path does not exists: \n{phoenix_log_path}")



def read_my_logs():
    print("Nanominer:")
    get_nanominer()

    print("Phoenixminer:")
    get_phoenix_miner()



plv.phoenix_total_shares()
# get_nanominer_levin()