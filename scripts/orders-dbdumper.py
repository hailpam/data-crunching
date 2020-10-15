import argparse
import locale
import sys

from datetime import datetime

from model import *  
from sql import *
from common import *
from util import *


def parse_arguments():
    '''
        Parse input arguments. Passing the API key is defined as mandatory.
    '''
    parser = argparse.ArgumentParser(description='Exports all JSON orders data into CSV format and optionally into a SQLite DB.')
    parser.add_argument('-k', '--key', type=str, required=True, help='API key to be used to perform the REST request to the backend.')
    parser.add_argument('-l', '--locale', type=str, required=False, help='Specify the locale: it_IT for italian. Otherwise machine default one.')
    parser.add_argument('-p', '--path', type=str, required=True, help='Define datastore base path to csv/ and db/ folders (csv/ and db/ folders should be already created).')

    args = parser.parse_args()
    
    return args

def main():
    args = parse_arguments()
    if args.locale:
        locale.setlocale(locale.LC_ALL, args.locale)
    else:
        locale.setlocale(locale.LC_ALL, 'en_GB')
    datastore_path = args.path

    if not is_path_existent('%s/%s' % (datastore_path, 'csv')):
        sys.exit(1)
    if not is_path_existent('%s/%s' % (datastore_path, 'db')):
        sys.exit(1)
    
    orders = load_orders_database(args.key)
    print('info: loaded %d order(s)...' % len(orders))
    print(orders[0])
    print('info: all records between FIRST and LAST\n')
    print(orders[-1])
    
    export_to_csv(orders, datastore_path)
    print('info: CSV export successul %d order(s)' % len(orders))

    export_to_sqlite(orders, datastore_path)

if __name__ == "__main__":
    main()
