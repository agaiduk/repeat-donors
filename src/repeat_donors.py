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

    # Read in percentile value and convert it to a fraction of 1 for future use
    with open(percentile_fname, 'r') as percentile_f:
        percentile = float(percentile_f.readline()) / 100.
    percentile_f.closed

    data_f = open(data_fname, 'r')
    donors_f = open(donors_fname, 'w')

    donors = {}
    recipients = {}

    while True:
        data_line = data_f.readline()
        if not data_line:
            break
        record = data_line.split('|')

        # Skip lines with too few fields, not conforming to FEC specifications
        if len(record) < 21:
            continue

        # Skip record completely if it is a donation from a PAC, ...
        other_id = record[15]
        if other_id:
            continue

        # ... if organization name is missing, ...
        cmte_id = record[0]
        if not cmte_id:
            continue

        # ... if no donation amount is given, or if there are non-numerical characters/it is negative
        if not valid_float(record[14]):
            continue
        else:
            transaction_amt = float(record[14])

        # Process donor's name, zip code, and transaction date
        name = record[7]
        if not valid_name(name):
            continue

        zip_code = record[10]
        if not valid_zip(zip_code):
            continue
        else:
            zip_code = record[10][:5]

        transaction_dt = record[13]
        if not valid_date(transaction_dt):
            continue
        year = int(record[13][4:8])

        donor = (name, zip_code)

        # If the donor is not know, initialize the heap (current record will be digested in a jiffy...)
        if donors.get(donor) is None:
            donors[donor] = Donor()
        else:
            if donors[donor].year_min < year:  # year_min is the first element of the heap inside the Donor class
                # The known donor is repeat: S/he donated in any of the previous (but not the current!) years
                recipient_zip_year = (cmte_id, zip_code, year)
                if recipients.get(recipient_zip_year) is None:
                    recipients[recipient_zip_year] = Recipient()
                recipients[recipient_zip_year].add_donation(transaction_amt)
                percentile_value = recipients[recipient_zip_year].compute_percentile_value(percentile)
                donors_f.write("{}|{}|{}|{}|{}|{}\n".format(cmte_id, zip_code, year, percentile_value,
                                                            round(recipients[recipient_zip_year].total_donated),
                                                            recipients[recipient_zip_year].total_donations)
                              )

        donors[donor].add_donation(year)

    data_f.close()
    donors_f.close()


if __name__ == "__main__":
    find_repeat_donors(sys.argv)
