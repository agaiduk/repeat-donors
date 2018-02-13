# Repeat donor analytics tool

This is a solution to the [programming challenge](https://github.com/InsightDataScience/donation-analytics) for the Insight Data Engineering program. The problem was to design an efficient data ingestion/processing pipeline for identifying regions of the country with multiple repeat political donors, for targeted political advertising. The pipeline designed in this work using Python programming language (v.3.6.3) will be the back-end of the donation analytics toolkit.

## Table of contents
1. [Summary of the problem](README.md#summary-of-the-problem)
2. [Solution summary](README.md#solution-summary)
    * [Run instructions](README.md#run-instructions)
    * [Code structure](README.md#code-structure)
3. [Algorithm highlights](README.md#algorithm-highlights)
4. [Requirements and dependencies](README.md#requirements-and-dependencies)
5. [Testing](README.md#tests)
    * [Scaling](README.md#scaling)

## Summary of the problem

* There are two input files: `itcont.txt` contains the [historical donation records](http://classic.fec.gov/finance/disclosure/ftpdet.shtml) that need to be processed and `percentile.txt` contains the percentile value for analyzing the donations received by a specific political entity in a given year from a given zip code;
* The pipeline needs to be designed for ingesting and processing *streaming* data, possibly in real time;
* The fields of interest in each record are `CMTE_ID` (the recipient of the contribution), `NAME` (donor name), `ZIP_CODE` (donor zip code), `TRANSACTION_DT` (transaction date), `TRANSACTION_AMT` (donation amount), and `OTHER_ID` (identifies PACs). Each record must be assessed to identify and reject records with empty or malformed fields, according to the Federal Election Commission [specifications](http://classic.fec.gov/finance/disclosure/metadata/DataDictionaryContributionsbyIndividuals.shtml);
* The data pipeline needs to be fast and scale well to large amount of data.

The current solution addresses all these concerns. Thanks to efficient algorithms and data structures, this code processes 1 million of randomized donation records in under 10 seconds and has [linear scaling](README.md#scaling) with the dataset size.

## Solution summary

### Run instructions

The code can be executed with the bash script `run.sh` in the root directory (set permissions with `chmod +x ./run.sh`) or by running:

```bash
$ python3 ./src/repeat_donors.py ./input/itcont.txt ./input/percentile.txt ./output/repeat_donors.txt
```

### Code structure

The code checks if input files `./input/itcont.txt` and `./input/percentile.txt` exist and raises exception if they don't; it also checks if the output directory `./output` exists. If there is a file `repeat_donors.txt` in `./output`, it is rewritten.

The `itcont.txt` file is read using a set of commands:

```python
data_f = open(data_fname, 'r')
while True:
    data_line = data_f.readline()
    if not data_line:
        break
```

This particular choice of commands allows for extending the algorithm to streaming data, for example, by modifying the `if not data_line` statement. Each record is then processed and retained only if all of the following conditions are satisfied:

* `CMTE_ID` exists;
* `NAME` is not empty and does not contain numbers and characters from the following list: ```~!@#$%^&*()?/\{}[]<>|+=:;```. Name field may, however, contain commas, dots, apostrophes, and quotation marks;
* `ZIP_CODE` can be converted to a positive integer of more than 5 digits, though only first 5 digits are used;
* `TRANSACTION_DT` can be converted to a positive integer (exactly 8 digits) that conforms to the [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) date format. There was no requirement to reject records if they referred to the date in the future or before 1974, when the Federal Elections Committee was founded, although these checks could be trivially implemented if desired;
* `TRANSACTION_AMT` can be represented as a positive floating point number. The assignment asked to check only if the `TRANSACTION_AMT` field existed but in real FEC data, some of the values are negative and others contain non-numerical characters, so these extra checks are warranted;
* `OTHER_ID` does not exist.

No checks are currently performed for whitespace-padded fields in the interest of performance, since such operations would slow down the algorithm. These extra checks could be implemented using standard Python libraries for operations with strings.

Each acceptable record is checked against the `donors` dictionary containing unique donors. Each donor's key is a tuple `(name, zip_code)`, providing a unique identifier as per this challenge. The donors in the dictionary are represented by objects of the `Donor()` class, containing a `heap` of years each donor has made political contributions. For the purpose of this challenge, a donor is considered to be "repeat" *only* if s/he has contributed to any recipient listed in the itcont.txt file in any *prior* calendar year. I.e., if the donor contributed multiple times during the current year (current = as in the record currently being processed) but not in any of the previous years, s/he will be treated as non-repeat in the current year.

The output of the code - summary of donations for a recipient `CMTE_ID` that came from a given zip code in a given year - is stored in the `recipients` dictionary, identified by the tuple `(cmte_id, zip_code, year)`. Each of these output "bins" is an object of the `Recipient()` class containing the list of donations, the total amount donated, and the number of donations. The calculation of donation values for a given percentile is done using the [nearest-rank method](https://en.wikipedia.org/wiki/Percentile#The_nearest-rank_method) using the `Recipient.compute_percentile_value(percentile)` function. The processed data is continuously accumulated in the `./output/repeat_donors.txt` file. The challenge asks to round the percentile value to the whole dollar; I also decided to round the sums of contributions, since this is how they were  (even though individual contributions can have 

## Algorithm highlights

* Dictionaries for donor/recipient look-up;
* Identifying each donor and recipient using tuples;
* Heaps for efficient look-up of the year a donor has made the first donation;
* Efficient nearest-rank percentile calculation using binary search algorithm for adding new contributions into sorted donations' lists;
* Classes representing donors and recipients.

## Requirements and dependencies

This package has been written for and tested with Python 3.6.3 interpreter, mostly using standard libraries: `sys`, `os`, `re`, `heapq`, `bisect`, and `math`. This package depends on the following package listed in the `requirements.txt` file in the root directory:

* `ciso8601 == 1.0.7`

This [dependency](https://pypi.python.org/pypi/ciso8601) may be installed by running:

```bash
$ pip install -r requirements.txt
```

or

```bash
$ pip install ciso8601
```

## Testing

The `insight_testsuite` folder contains several datasets I used to test my code. Folders `test_1` and `test_2` in `insight_testsuite/tests` directory are based on the data in the challenge and the FAQs; folders `test_3` through `test_6` contain real randomized FEC data with 5,000, 10,000, and 100,000 records from the data files for the [2015-2016](https://cg-519a459a-0ea3-42c2-b7bc-fa1143481f74.s3-us-gov-west-1.amazonaws.com/bulk-downloads/2016/indiv16.zip) and [2017-2018](https://cg-519a459a-0ea3-42c2-b7bc-fa1143481f74.s3-us-gov-west-1.amazonaws.com/bulk-downloads/2018/indiv18.zip) election cycles. The data sets were prepared using Unix `shuf` command as follows:

```bash
$ cat itcont_2015-2016.txt itcont_2017-2018.txt > itcont_2015-2018.txt
$ shuf -n N itcont_2015-2018.txt > itcont.txt
```

`N` is the target number of records in the test data file.

To run tests, switch to the `insight_testsuite` and run the `run_tests.sh` script:

```
$ ./run_tests.sh
[PASS]: test_1 repeat_donors.txt
[PASS]: test_2 repeat_donors.txt
[PASS]: test_3 repeat_donors.txt
[PASS]: test_4 repeat_donors.txt
[PASS]: test_5 repeat_donors.txt
[PASS]: test_6 repeat_donors.txt
[Tue Feb 13 01:17:27 CST 2018] 6 of 6 tests passed
```

### Scaling
In addition to the tests contained in the repository, tests for data sets with up to 27.4 million records (randomized full content of the FEC individual donations archive in 2015-2018, ~5 Gb of data) were conducted to understand the scaling of the algorithm:

|     #, records     |      Time, s          |
| -------------|-------------:| 
| 5,000        | 0.1 |
| 10,000       | 0.13 |
| 100,000      | 0.7 |
| 1,000,000    | 8  |
| 2,000,000    | 15 |
| 4,000,000    | 35 |
| 27,385,013   | 230 |


The algorithm has linear scaling with the number of records; hence it is suitable for the analysis of large data sets.
