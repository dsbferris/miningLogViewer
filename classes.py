import logging
from datetime import datetime, timedelta
import requests
import pathlib
from colorama import Fore

class ShareClass(object):
    accepted_shares: int
    rejected_shares: int

    def __init__(self, accepted=0, rejected=0):
        self.accepted_shares = accepted
        self.rejected_shares = rejected

    def __add__(self, other):
        return ShareClass(accepted=self.accepted_shares + other.accepted_shares,
                          rejected=self.rejected_shares + other.rejected_shares)

    def __sub__(self, other):
        if self.accepted_shares > other.accepted_shares or self.rejected_shares > other.rejected_shares:
            return ShareClass(accepted=(self.accepted_shares - other.accepted_shares),
                              rejected=(self.rejected_shares - other.rejected_shares))
        else:
            return ShareClass(accepted=(other.accepted_shares - self.accepted_shares),
                              rejected=(other.rejected_shares - self.rejected_shares))

    def __str__(self):
        return f"Accepted: {self.accepted_shares}, Rejected: {self.rejected_shares}"


class LogEvalClass:
    payout_worked_for: datetime
    runtime: timedelta
    shares: ShareClass

    def __init__(self, payout_worked_for: datetime = datetime.min, runtime=timedelta(0),
                 shares: ShareClass = ShareClass()):
        self.payout_worked_for = payout_worked_for
        self.shares = shares
        self.runtime = runtime

    def get_power_cost(self, wattage: int, kwh_price: float) -> float:
        hours = self.runtime.total_seconds() / 3600
        kilo_wattage = wattage / 1000
        kwh = kilo_wattage * hours
        cost = kwh * kwh_price
        cost = round(cost, 2)
        return cost

    def get_power_cost_string(self, wattage: int, kwh_price: float) -> str:
        return f"At {wattage}W at {'{:0,.2f}'.format(kwh_price)}€/KWh: {'{:0,.2f}'.format(self.get_power_cost(wattage=wattage, kwh_price=kwh_price))}€"

    def __str__(self):
        return f"For Payout: {self.payout_worked_for.isoformat(' ', 'seconds')}, " \
               f"Runtime: {str(self.runtime).split('.')[0]}, " \
               f"{self.shares}"

    def __add__(self, other):
        if self.payout_worked_for != other.payout_worked_for:
            print(Fore.RED + "You should not add different payouts!" + Fore.RESET)

        return LogEvalClass(payout_worked_for=self.payout_worked_for,
                            shares=(self.shares + other.shares),
                            runtime=(self.runtime + other.runtime))
