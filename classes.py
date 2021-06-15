from datetime import datetime, timedelta
import requests
import pathlib


class ShareClass(object):
    accepted_shares: int
    rejected_shares: int

    def __init__(self, accepted=0, rejected=0):
        self.accepted_shares = accepted
        self.rejected_shares = rejected

    def __add__(self, other):
        return ShareClass(accepted=self.accepted_shares + other.accepted_shares,
                          rejected=self.rejected_shares + other.rejected_shares)

    # def __radd__(self, other):
    #     if other == 0:
    #         return self
    #     else:
    #         return self.__add__(other)

    def __sub__(self, other):
        if self.accepted_shares > other.accepted_shares or self.rejected_shares > other.rejected_shares:
            return ShareClass(accepted=(self.accepted_shares - other.accepted_shares),
                              rejected=(self.rejected_shares - other.rejected_shares))
        else:
            return ShareClass(accepted=(other.accepted_shares - self.accepted_shares),
                              rejected=(other.rejected_shares - self.rejected_shares))

    # def __rsub__(self, other):
    #     if other == 0:
    #         return self
    #     else:
    #         return self.__sub__(other)

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

    def get_power_cost(self, wattage: int, cost_per_kwh_in_eur: float) -> float:
        hours = self.runtime.total_seconds() / 3600
        kilo_wattage = wattage / 1000
        kwh = kilo_wattage * hours
        cost = kwh * cost_per_kwh_in_eur
        return cost

    def __str__(self):
        return f"For Payout: {self.payout_worked_for.isoformat(' ', 'seconds')}, Runtime: {self.runtime}, {self.shares}"
