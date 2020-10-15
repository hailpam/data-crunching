import requests
import math
import time
import locale
import os
import sqlite3
import json

from datetime import datetime

from sql import *
from model import *

# Base URL to target the service.
BASE_URL = 'https://www.gestionalesmarty.com/titanium'
# Specific REST endpoint to invoke.
API_URI = 'V2/Api/Sales_Orders'
# Method to user upon a REST invokation.
METHOD = 'list'

# Data folders.
DB_FOLDER = 'db'
CSV_FOLDER = 'csv'

# Maximum number of items per REST call.
NR_RECORDS_LIMIT_PER_CALL = 50

def deserialize(orders, loaded_orders):
    '''
        Convert JSON orders into an in-memory deserialized version.
    '''
    for order in orders:
        c = Customer(order['billing_address']['name'], order['billing_address']['address'], order['billing_address']['zipcode'], order['billing_address']['city'], order['billing_address']['state'], order['billing_address']['country_iso'], identifier=order['customer_id'])
        s = Shipment(order['weight'], order['shipping_date'], order['carrier'], order['shipped'], order['shipping_confirmed'], order['fees']['shipping'], order['fees']['payment'], order['fees']['extra'], order['locked'])
        o = Order(order['id'], order['date'], order['number'], order['code'], order['payment_type'], c, s)
        rows = order['rows']
        for row in rows:
            i = Item(row['id'], row['sku'], row['name'], row['price'], row['discount'], row['tax_id'], row['tax'], row['quantity'])
            o.items.append(i)
        loaded_orders.append(o)

def find_last_order(api_key):
    '''
        Find the last inserted order. According to its ID, the database is going to be rebuilt.
    '''
    params = 'limit=%d&offset=%d' % (1, 0)
    res = retryable_get(BASE_URL, API_URI, METHOD, api_key, params)
    orders = json.loads(res.text)
    if res.status_code != 200 or 'error' in res.text:
        print('error: not able to fetch data: %s' % res.text)
        raise Exception(res.text)
    
    return int(orders[0]['id'])

def load_orders_database(api_key):
    '''
        Load orders incrementally the entire database up. It transforms it into an internal format which is then re-used for export.
    '''
    loaded_orders = []

    iterations = math.ceil(find_last_order(api_key) / NR_RECORDS_LIMIT_PER_CALL)
    for itr in range(iterations):
        s = int(time.time() * 10**3)
        params = 'limit=%d&offset=%d' % (NR_RECORDS_LIMIT_PER_CALL, itr * NR_RECORDS_LIMIT_PER_CALL)
        res = retryable_get(BASE_URL, API_URI, METHOD, api_key, params)
        
        print('info: iteration %d out of %d: took %dms' % (itr+1, iterations, int(time.time() * 10**3) - s))
        
        orders = json.loads(res.text)
        if res.status_code != 200 or 'error' in res.text:
            print('error: not able to fetch data: %s' % res.text)
            raise Exception(res.text)
        
        deserialize(orders, loaded_orders)
        
    return loaded_orders

def load_orders_pages(api_key, nr_records):
    '''
        Load the orders data up. It transforms it into an internal format which is then re-used for export.
    '''
    loaded_orders = []
    
    iterations = math.ceil(nr_records / NR_RECORDS_LIMIT_PER_CALL)
    for itr in range(iterations):
        s = int(time.time() * 10**3)
        params = 'limit=%d&offset=%d' % (NR_RECORDS_LIMIT_PER_CALL, itr * NR_RECORDS_LIMIT_PER_CALL)
        res = retryable_get(BASE_URL, API_URI, METHOD, api_key, params)
        
        print('info: iteration %d out of %d: took %dms' % (itr+1, iterations, int(time.time() * 10**3) - s))
        
        orders = json.loads(res.text)
        if res.status_code != 200 or 'error' in res.text:
            print('error: not able to fetch data: %s' % res.text)
            raise Exception(res.text)
        
        deserialize(orders, loaded_orders)
        
    return loaded_orders

def load_customers(api_key):
    '''
        Load customer data up. It transforms it into an internal format which is then re-used for export.
    '''
    loaded_customers = []

def export_to_csv(orders, base_path):
    '''
        Export the internal deserialized version of the data into a CSV file. The CSV file can be then reused with Excel or compatible
        programs to create pivot tables and so analytics.
    '''
    try:
        now = datetime.now()
        csv_name = '%s/%s/%s_%s_export.csv' % (base_path, CSV_FOLDER, now.strftime('%Y%m%d_%H%M%S'), locale.getlocale()[0])
        f = open(csv_name, 'w')
        header = False
        for order in orders:
            for item in order.items:
                if not header:
                    f.write('%s,%s,%s,%s\n' % (order.to_header(), order.customer.to_header(), item.to_header(), order.shipment.to_header()))
                    header = True
                f.writelines('%s,%s,%s,%s\n' % (order.to_csv(), order.customer.to_csv(), item.to_csv(), order.shipment.to_csv()))
    except Exception as e:
        print('error: unable to export to CSV: %s' % e)
    finally:
        if f:
            f.close()

def create_sqlite_db(db_name, base_path):
    '''
        Make sure that a DB file is created in case of non-existence. Create the table.
    '''
    print('info: creating the DB...')
    path = '%s/%s/' % (base_path, DB_FOLDER)
    try:
        os.stat(path)
    except:
        os.mkdir(path)
    
    try:
        conn = sqlite3.connect('%s/%s' % (path, db_name))
        conn.execute(SQL_CREATE_TABLE)
    finally:
        if conn:
            conn.commit()
            conn.close()

def drop_sqlite_db(db_name, base_path):
    '''
        Make sure that a DB file is created in case of non-existence. Drop the table in case of existence.
    '''
    print('info: dropping the DB...')
    path = '%s/%s/' % (base_path, DB_FOLDER)
    try:
        os.stat(path)
    except:
        os.mkdir(path)
    
    try:
        conn = sqlite3.connect('%s/%s' % (path, db_name))
        res = conn.execute(SQL_DROP_TABLE)
    finally:
        if conn:
            conn.commit()
            conn.close()

def export_to_sqlite(orders, base_path):
    '''
        Export the internal deserialized version of the data into a SQLite database. The SQLite database can be then re-used from Excel
        using an ODBC connection: data can be sliced and diced using simple but effective Pivot tables.
    '''
    db_name = 'orders_%s.db' % locale.getlocale()[0]
    db_path = '%s/%s/%s' % (base_path, DB_FOLDER, db_name)
    try:
        os.stat(db_path)
    except:
        create_sqlite_db(db_name, base_path)
    
    try:
        conn = sqlite3.connect(db_path)
        rows = conn.execute(SQL_SELECT_DISTINCT_ID)
        ids = set()
        for row in rows:
            ids.add(row[0])
        cntr = 0
        for order in orders:
            for item in order.items:
                if order.id in ids:
                    cntr += 1
                    conn.execute(delete_records(order))
                    ids.remove(order.id)
                conn.execute(insert_record(order, item))
        if cntr > 0:
            print('warning: %s row(s) were duplicated: update was made' % cntr)
        
        print('info: SQLite loaded successfully with %d record(s)' % len(orders))
    except Exception as e:
        print('error: unable to load SQLite database: %s' % e)
    finally:
        if conn:
            conn.commit()
            conn.close()

def is_path_existent(path):
    '''
        Check whether a path is already existent.
    '''
    try:
        os.stat(path)
        return True
    except:
        print('error: [%s] is not existent' % path)
        return False

def retryable_get(url, uri, method, key, params):
    '''
        Retries on network glitches. Instead of giving up and abandoning, it backs off to then retry
        in a number of seconds proportial to the number of attempts.
    '''
    errors = 0
    while True:
        try:
            res = requests.get('%s/%s/%s?ApiKey=%s&%s' % (url, uri, method, key, params))
            return res
        except Exception as e:
            errors += 1
            print('error: an exception was thrown: %s' % e)
            print('warning: backing off %d seconds prior to retry...' % errors)
            time.sleep(errors)
