import argparse
import locale

from datetime import datetime

from model import *  
from sql import *
from common import *

def parse_arguments():
    '''
        Parse input arguments. Passing the API key is defined as mandatory.
    '''
    parser = argparse.ArgumentParser(description='Incrementally exports JSON orders data into CSV format and optionally into a SQLite DB.')
    parser.add_argument('-k', '--key', type=str, required=True, help='API key to be used to perform the REST request to the backend')
    parser.add_argument('-l', '--locale', type=str, required=False, help='Specify the locale: it_IT for italian. Otherwise machine default one.')
    parser.add_argument('-d', '--db', action='store_true', required=False, help='Instruct the tool to load a SQLite database up')
    parser.add_argument('-p', '--path', type=str, required=True, help='Define datastore base path (CSV and SQLite archive will be based out of it)')
    parser.add_argument('-n', '--number', type=int, required=True, help='Define how many records each REST call should pull down')
    args = parser.parse_args()
    
    return args

def main():
    args = parse_arguments()
    if args.locale:
        locale.setlocale(locale.LC_ALL, args.locale)
    else:
        locale.setlocale(locale.LC_ALL, 'en_GB')
    datastore_path = args.path
    nr_records = args.number

    # orders = load_data(args.key, nr_records)
    orders = load_database(args.key)
    print('info: loaded %d order(s)...' % len(orders))
    for order in orders:
        print(order)
    
    export_to_csv(orders, datastore_path)
    print('info: CSV export successul %d order(s)' % len(orders))

    if args.db:
        export_to_sqlite(orders, datastore_path)

if __name__ == "__main__":
    main()
