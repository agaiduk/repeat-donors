from datetime import datetime


def valid_name(string):
    return True


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


# This function is VERY slow; replace it by ciso8601 in future commits
def valid_date(string):
    try:
        datetime.strptime(string, '%m%d%Y')
        return True
    except ValueError:
        return False


data_fname = '../input/itcont.txt'
percentile_fname = '../input/percentile.txt'

try:
    data_f = open(data_fname, 'r')
    percentile_f = open(percentile_fname, 'r')
except IOError:
    print("Error while trying to access files.")

percentile = int(percentile_f.readline())
percentile_f.close()

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
        zip_code = int(line[10][:5])

    transaction_dt = line[13]
    if not valid_date(transaction_dt):
        continue

data_f.close()
