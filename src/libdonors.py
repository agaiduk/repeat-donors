import os
import ciso8601
import re
import heapq
import bisect
from math import ceil


def input_check(fname):
    if os.path.isfile(fname) is False:
        raise AssertionError("Input file {} does not exist".format(os.path.abspath(fname)))


def output_check(fname):
    fname_abspath = os.path.abspath(fname)
    dirname = os.path.dirname(fname_abspath)
    if os.path.isdir(dirname) is False:
        raise AssertionError("Output directory {} does not exist".format(dirname))
    if os.path.isfile(fname) is True:
        print("File {} exist; overwriting.".format(fname_abspath))
        open(fname_abspath, 'w').close()  # Erase existing output file - performance improvement


# Checks that the name is not empty and that it doesn't contain special
# characters (except for "-", quotes, dot, and comma)
# OVERHEAD: 1-2 s per million records
# Not compiling regular expression actually makes it run a bit faster
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


# True a string is a positive float (or a positive integer); for donations amount
def valid_float(string):
    try:
        number = float(string)
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


def valid_date(string):
    if len(string) != 8:
        return False
    yyyymmdd = string[4:] + string[:2] + string[2:4]  # string is in mmddyyyy format
    return bool(ciso8601.parse_datetime(yyyymmdd))


class Donor:

    def __init__(self):
        self.years = []
        self.year_min = float("inf")

    def add_donation(self, year):
        heapq.heappush(self.years, year)
        self.year_min = self.years[0]


class Recipient:

    def __init__(self):
        self.donations = []
        self.total_donated = 0.
        self.total_donations = 0

    def add_donation(self, donation):
        bisect.insort(self.donations, donation)
        self.total_donated += donation
        self.total_donations += 1

    def compute_percentile(self, percentile):
        assert 0 <= percentile <= 1, "Percentile in Recipient.compute_percentile() must be a fraction of 1"
        percentile_value = self.total_donations * percentile
        ordinal_rank = ceil(percentile_value)
        if ordinal_rank == 0:
            ordinal_rank = 1
        return round(self.donations[ordinal_rank - 1])  # -1 to account for Python array numbering
