data_fname = '../input/itcont.txt'
percentile_fname = '../input/percentile.txt'

data_f = open(data_fname, 'r')
percentile_f = open(percentile_fname, 'r')

percentile = int(percentile_f.readline())

while True:
    data_line = data_f.readline()
    if not data_line:
        break
    line = data_line.split('|')

data_f.close()
percentile_f.close()
