import sys
from libdonors import input_check, output_check, valid_name, valid_date, valid_zip, valid_float
from libdonors import Donor, Recipient


def find_repeat_donors(argv):

    if len(argv) < 3:
        raise AssertionError("Usage: repeat_donors.py <data_file> <percentile_file> <output_file>")

    data_fname = argv[1]
    percentile_fname = argv[2]
    donors_fname = argv[3]

    input_check(data_fname)
    input_check(percentile_fname)
    output_check(donors_fname)

    data_f = open(data_fname, 'r')
    percentile_f = open(percentile_fname, 'r')
    donors_f = open(donors_fname, 'w')

    # Read in percentile value and convert it to a fraction of 1 for future use
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

        # Transaction amount
        if not valid_float(line[14]):
            continue
        else:
            transaction_amt = float(line[14])

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
        year = int(line[13][4:8])

        donor = (name, zip_code)
        # If the donor is not know, initialize the heap and add the year to it
        if donors.get(donor) is None:
            donors[donor] = Donor()
        else:
            if donors[donor].year_min < year:  # year_min is the first element of the heap inside Donor class
                # The known donor is repeat: S/he donated in any of the previous (but not current) years
                recipient_zip_year = (cmte_id, zip_code, year)
                if recipients.get(recipient_zip_year) is None:
                    recipients[recipient_zip_year] = Recipient()
                recipients[recipient_zip_year].add_donation(transaction_amt)
                percentile_value = recipients[recipient_zip_year].compute_percentile(percentile)
                donors_f.write("{}|{}|{}|{}|{}|{}\n".format(cmte_id, zip_code, year, percentile_value, round(recipients[recipient_zip_year].total_donated), recipients[recipient_zip_year].total_donations))
        donors[donor].add_donation(year)
    data_f.close()
    percentile_f.close()
    donors_f.close()


if __name__ == "__main__":
    find_repeat_donors(sys.argv)
