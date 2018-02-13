import os
import ciso8601
import re
import heapq
import bisect
from math import ceil


def input_check(fname):
    ''' Checks that the input file fname exists '''
    if os.path.isfile(fname) is False:
        raise AssertionError("Input file {} does not exist".format(os.path.abspath(fname)))


def output_check(fname):
    ''' Checks that the directory for the output file fname exists
        If the output file fname exists, it is overwritten '''
    fname_abspath = os.path.abspath(fname)
    dirname = os.path.dirname(fname_abspath)
    if os.path.isdir(dirname) is False:
        raise AssertionError("Output directory {} does not exist".format(dirname))
    if os.path.isfile(fname) is True:
        print("File {} exist; overwriting.".format(fname_abspath))
        open(fname_abspath, 'w').close()  # Erase existing output file here --> performance improvement


def valid_name(string):
    ''' Checks that the name is not empty and that it doesn't contain special characters
        (except for "-", quotes, dot, and comma, which all can be part of a real name) '''
    if len(string) < 1:
        return False
    return not bool(re.search(r'[\[\]0-9~!@#$%^&*()?/\\{}<>|+=:;]', string))


def valid_int(string):
    ''' True for a string that represents a positive integer '''
    try:
        number = int(string)
        return (number > 0)
    except ValueError:
        return False


def valid_float(string):
    ''' True for a string that represents a positive float (or a positive integer) - for donation amount '''
    try:
        number = float(string)
        return (number > 0)
    except ValueError:
        return False


def valid_zip(string):
    ''' Discard zip if not a positive integer (e.g. exclude Canadian postal codes) '''
    if not valid_int(string):
        return False
    if len(string) < 5:
        return False
    else:
        return True


def valid_date(string):
    ''' Check that the date is an 8-digit integer and conforms to ISO 8601 '''
    if len(string) != 8:
        return False
    yyyymmdd = string[4:] + string[:2] + string[2:4]  # string is in mmddyyyy format
    return bool(ciso8601.parse_datetime(yyyymmdd))


class Donor:
    ''' Class defining a donor with the heapified list of years donated
        year_min is the first element of the heap which is the smallest year '''
    def __init__(self):
        self.years = []
        self.year_min = float("inf")

    def add_donation(self, year):
        heapq.heappush(self.years, year)
        self.year_min = self.years[0]


class Recipient:
    ''' Class defining a recipient with a sorted list of donations '''
    def __init__(self):
        self.donations = []
        self.total_donated = 0.
        self.total_donations = 0

    def add_donation(self, donation):
        ''' Add donation using binary search method and update counters '''
        bisect.insort(self.donations, donation)
        self.total_donated += donation
        self.total_donations += 1

    def compute_percentile_value(self, percentile):
        ''' Compute percentile using nearest-rank method '''
        if not 0 <= percentile <= 1:
            raise AssertionError("Percentile in Recipient.compute_percentile() must be a fraction of 1")
        ordinal_rank = ceil(self.total_donations * percentile)
        if ordinal_rank == 0:
            ordinal_rank = 1
        return round(self.donations[ordinal_rank - 1])  # -1 to account for Python array numbering
