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


def compute_percentile(array, length, percentile):
    # percentile should be a fraction of 1; length should be supplied to avoid computing it
    percentile_value = length * percentile
    ordinal_rank = ceil(percentile_value)
    return array[ordinal_rank - 1]  # -1 to account for Python array numbering


data_fname = './input/itcont.txt'
percentile_fname = './input/percentile.txt'
donors_fname = './output/repeat_donors.txt'

data_f = open(data_fname, 'r')
percentile_f = open(percentile_fname, 'r')
donors_f = open(donors_fname, 'w')

percentile = float(percentile_f.readline()) / 100.

donors = {}
recipients = {}

while True:
    data_line = data_f.readline()
    if not data_line:
        break
    line = data_line.split('|')

    # Skip lines with too few fields, not conforming to FEC specifications
    if len(line) < 21:
        continue

    # Skip record completely if it is a donation from a PAC; if political
    # organization name is missing, or if no donation amount is given
    # Test for cmte_id and transaction_amt below won't work if the fields
    # are strings of whitespaces; this can be done using 'if not string.replace(" ","")'
    # command, but it increases the execution time by a factor of ~9
    other_id = line[15]
    if other_id:
        continue

    cmte_id = line[0]
    if not cmte_id:
        continue

    transaction_amt = line[14]
    if not transaction_amt:
        continue

    # Process donor's name, zip code, and transaction date
    name = line[7]
    if not valid_name(name):
        continue

    zip_code = line[10]
    if not valid_zip(zip_code):
        continue
    else:
        zip_code = line[10][:5]

    transaction_dt = line[13]
    if not valid_date(transaction_dt):
        continue
    year = line[13][4:8]

    donor = (name, zip_code)
    # If the donor is not know, initialize the heap and add the year to it
    if donors.get(donor) is None:
        donors[donor] = []
        heapq.heappush(donors[donor], year)
    else:
        # The known donor is not repeat: S/he only donated in the current or future year
        if donors[donor][0] >= year:
            heapq.heappush(donors[donor], year)
        # Repeat donor
        else:
            recipient_zip_year = (cmte_id, zip_code, year)
            if recipients.get(recipient_zip_year) is None:
                recipients[recipient_zip_year] = []
            heapq.heappush(recipients[recipient_zip_year], int(transaction_amt))
            total_num = len(recipients[recipient_zip_year])
            total_amt = sum(recipients[recipient_zip_year])
            percentile_value = compute_percentile(recipients[recipient_zip_year], total_num, percentile)
            donors_f.write("{}|{}|{}|{}|{}|{}\n".format(cmte_id, zip_code, year, percentile_value, total_amt, total_num))

data_f.close()
percentile_f.close()
donors_f.close()
