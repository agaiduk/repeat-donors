from datetime import datetime
import re
import heapq
from math import ceil


# Checks that the name is not empty and that it doesn't contain special
# characters (except for "-", quotes, dot, and comma)
# OVERHEAD: 1-2 s per million records
# Not compiling the regular expression makes it run 10-20% faster
def valid_name(string):
    if len(string) < 1:
        return False
    return not bool(re.search(r'[\[\]0-9~!@#$%^&*()?/\\{}<>|+=:;]', string))


# True for a string that is a positive integer
def valid_int(string):
    try:
        number = int(string)
        return (number > 0)
    except ValueError:
        return False


def valid_zip(string):
    # Discard if not an integer (e.g. exclude Canadian postal codes)
    if not valid_int(string):
        return False
    if len(string) < 5:
        return False
    else:
        return True


# This function is very slow: Adds ~10 seconds per million records
# Will replace it by ciso8601 in future commits
def valid_date(string):
    try:
        datetime.strptime(string, '%m%d%Y')
        return True
    except ValueError:
        return False


class Donor:

    def __init__(self):
        self.years = []
        self.year_min = 0

    def add_donation(self, year):
        heapq.heappush(self.years, year)
        self.year_min = self.years[0]


class Recipient:

    def __init__(self):
        self.donations = []
        self.donations_amount = 0.
        self.donations_number = 0

    def add_donation(self, donation):
        heapq.heappush(self.donations, donation)
        self.donations_amount += donation
        self.donations_number += 1

    def compute_percentile(self, percentile):
        assert 0 <= percentile <= 1, "Percentile in Recipient.compute_percentile() must be a fraction of 1"
        percentile_value = self.donations_number * percentile
        ordinal_rank = ceil(percentile_value)
        if ordinal_rank == 0:
            ordinal_rank = 1
        return round(sorted(self.donations)[ordinal_rank - 1])  # -1 to account for Python array numbering
