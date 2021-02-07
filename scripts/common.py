import math
import time
import locale
import os
import sqlite3
import json
import traceback

from datetime import datetime

from sql import *
from model import *
from util import *

# Base URL to target the service.
BASE_URL = 'https://www.gestionalesmarty.com/titanium'
# Specific REST endpoint to invoke.
ORDERS_API_URI = 'V2/Api/Sales_Orders'
CUSTOMERS_API_URI = 'V2/Api/Customers'
# Method to user upon a REST invokation.
METHOD = 'list'

# Data folders.
DB_FOLDER = 'db'
CSV_FOLDER = 'csv'

# Maximum number of items per REST call.
NR_RECORDS_LIMIT_PER_CALL = 50

def deserialize_orders(orders, loaded_orders, lookup):
    '''
        Convert JSON orders into an in-memory deserialized version.
    '''
    for order in orders:
        c = Customer(order['billing_address']['name'], order['billing_address']['address'], order['billing_address']['zipcode'], order['billing_address']['city'], order['billing_address']['state'], order['billing_address']['country_iso'], identifier=order['customer_id'])
        # got to enrich with attributes available from the Customers table
        if c.id in lookup:
            l = lookup[c.id]
            c.email = l.email
            c.phone = l.phone
            c.business_name = l.business_name
            c.created_at = l.created_at
            c.updated_at = l.updated_at
        s = Shipment(order['weight'], order['shipping_date'], order['carrier'], order['shipped'], order['shipping_confirmed'], order['fees']['shipping'], order['fees']['payment'], order['fees']['extra'], order['locked'], order['canceled'], order['locked'])
        o = Order(order['id'], order['date'], order['number'], order['code'], order['payment_type'], c, s, order['paid'], order['cod_value'], order['packages'], order['payments'])
        rows = order['rows']
        for row in rows:
            i = Item(row['id'], row['sku'], row['name'], row['price'], row['discount'], row['tax_id'], row['tax'], row['quantity'])
            o.items.append(i)
        loaded_orders.append(o)

def deserialize_customers(customers, loaded_customers):
    '''
        Convert JSON customers into an in-memory deserialized version.
    '''
    for customer in customers:
        name = customer['name'] +' '+ customer['last_name']
        address = customer['billing_address']['address']
        zipcode = customer['billing_address']['zipcode']
        city = customer['billing_address']['city']
        state = customer['billing_address']['state']
        country_iso = customer['billing_address']['country_iso']
        email = customer['email']
        identifier = customer['id']
        phone = customer['phone']
        business_name = customer['business_name']
        created_at = customer['created']
        updated_at = customer['last_update']

        c = Customer(name, address, zipcode, city, state, country_iso, email, identifier, phone, business_name, created_at, updated_at)
        loaded_customers.append(c)

def lookup_customers(base_path):
    '''
        Given the identifier, it looks up the customers from the database and keeps them in memory
        for successive access.
        It retuns a lookup map which can be used to enrich Orders data.
    '''
    db_name = 'orders_%s.db' % locale.getlocale()[0]
    db_path = '%s/%s/%s' % (base_path, DB_FOLDER, db_name)

    customers = {}
    try:
        conn = sqlite3.connect(db_path)
        rows = conn.execute(SQL_SELECT_ALL_CUSTOMERS)
        for row in rows:
            name = row[0]
            address = row[2]
            zipcode = row[3]
            city = row[4]
            state = row[5]
            country_iso = row[6]
            email = row[7]
            identifier = row[1]
            phone = row[8]
            business_name = row[9]
            created_at = row[10]
            updated_at = row[11]
            c = Customer(name, address, zipcode, city, state, country_iso, email, identifier, phone, business_name, created_at, updated_at) 
            customers[identifier] = c
    except Exception as e:
        print('error: it was not possible to lookup customers: %s' % e)
    finally:
        if conn:
            conn.close()

    return customers

def find_last_order(api_key):
    '''
        Find the last inserted order. According to its ID, the database is going to be rebuilt.
    '''
    params = 'limit=%d&offset=%d' % (1, 0)
    res = retryable_get(BASE_URL, ORDERS_API_URI, METHOD, api_key, params)
    
    if res.status_code != 200 or 'error' in res.text:
        print('error: not able to fetch data: %s' % res.text)
        raise Exception(res.text)
    
    orders = json.loads(res.text)

    return int(orders[0]['id'])

def load_orders_database(api_key, lookup):
    '''
        Load orders incrementally the entire database up. It transforms it into an internal format which is then re-used for export.
    '''
    loaded_orders = []

    iterations = math.ceil(find_last_order(api_key) / NR_RECORDS_LIMIT_PER_CALL)
    for itr in range(iterations):
        timer = Timer(time.time())
        params = 'limit=%d&offset=%d' % (NR_RECORDS_LIMIT_PER_CALL, itr * NR_RECORDS_LIMIT_PER_CALL)
        res = retryable_get(BASE_URL, ORDERS_API_URI, METHOD, api_key, params)
        
        print('info: iteration %d out of %d: took %dms' % (itr+1, iterations, timer.elapsed_ms()))
        if res.status_code != 200 or 'error' in res.text:
            print('error: not able to fetch data: %s' % res.text)
            raise Exception(res.text)

        orders = json.loads(res.text)
        deserialize_orders(orders, loaded_orders, lookup)
        
    return loaded_orders

def load_orders_pages(api_key, nr_records, lookup):
    '''
        Load the orders data up. It transforms the data into an internal format which is then re-used for export.
    '''
    loaded_orders = []
    
    iterations = math.ceil(nr_records / NR_RECORDS_LIMIT_PER_CALL)
    for itr in range(iterations):
        timer = Timer(time.time())
        params = 'limit=%d&offset=%d' % (NR_RECORDS_LIMIT_PER_CALL, itr * NR_RECORDS_LIMIT_PER_CALL)
        res = retryable_get(BASE_URL, ORDERS_API_URI, METHOD, api_key, params)
        
        print('info: iteration %d out of %d: took %dms' % (itr+1, iterations, timer.elapsed_ms()))
        if res.status_code != 200 or 'error' in res.text:
            print('error: not able to fetch data: %s' % res.text)
            raise Exception(res.text)
        
        orders = json.loads(res.text)
        deserialize_orders(orders, loaded_orders, lookup)
        
    return loaded_orders

def load_customers_pages(api_key, nr_cycles):
    '''
        Load the customers data up. It transforms the data into an internal format which is then re-used for export.
    '''
    loaded_customers = []
    for itr in range(nr_cycles):
        timer = Timer(time.time())
        params = 'limit=%d&offset=%d' % (NR_RECORDS_LIMIT_PER_CALL, itr * NR_RECORDS_LIMIT_PER_CALL)
        res = retryable_get(BASE_URL, CUSTOMERS_API_URI, METHOD, api_key, params)

        print('info: iteration %d out of %d: took %dms' % (itr+1, nr_cycles, timer.elapsed_ms()))
        if res.status_code != 200 or 'error' in res.text:
            print('error: not able to fetch data: %s' % res.text)
            raise Exception(res.text)
        
        customers = json.loads(res.text)
        if len(customers) == 0:
            print('warning: got to have 0 customers, so far retrieved %d customer(s)' % len(loaded_customers))
            return loaded_customers

        deserialize_customers(customers, loaded_customers)
    
    print('info: laoded %d customer(s)' % len(loaded_customers))

    return loaded_customers

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
        traceback.print_exc()
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
        conn.execute(SQL_CREATE_TABLE_ORDERS)
        conn.execute(SQL_CREATE_TABLE_CUSTOMERS)
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
        res = conn.execute(SQL_DROP_TABLE_ORDERS)
        res = conn.execute(SQL_DROP_TABLE_CUSTOMERS)
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
        rows = conn.execute(SQL_SELECT_DISTINCT_ID_ORDERS)
        ids = set()
        for row in rows:
            ids.add(int(row[0]))
        cntr = 0
        for order in orders:
            for item in order.items:
                if int(order.id) in ids:
                    cntr += 1
                    conn.execute(delete_records_orders(order))
                    ids.remove(order.id)
                conn.execute(insert_record_orders(order, item))
        if cntr > 0:
            print('warning: %s row(s) were duplicated: update was made' % cntr)
        
        print('info: SQLite loaded successfully with %d record(s)' % len(orders))
    except Exception as e:
        print('error: unable to load SQLite database: %s' % e)
    finally:
        if conn:
            conn.commit()
            conn.close()

def persist_customers_to_sqlite(customers, base_path):
    """
        Persist retrieved customers into SQLite table for successive lookup.
    """
    db_name = 'orders_%s.db' % locale.getlocale()[0]
    db_path = '%s/%s/%s' % (base_path, DB_FOLDER, db_name)
    try:
        os.stat(db_path)
    except:
        create_sqlite_db(db_name, base_path)
    
    try:
        conn = sqlite3.connect(db_path)
        rows = conn.execute(SQL_SELECT_DISTINCT_ID_CUSTOMERS)
        ids = set()
        for row in rows:
            ids.add(int(row[0]))
        cntr = 0
        for customer in customers:
            try:
                if int(customer.id) in ids:
                    cntr += 1
                    conn.execute(update_records_customers(customer))
                else:
                    conn.execute(insert_record_customers(customer))
            except Exception as e:
                print('error: client [%s] cannot be inserted: %s' % (customer, e))
        if cntr > 0:
            print('warning: %s row(s) were duplicated: update was made' % cntr)
        
        print('info: SQLite persisted successfully %d Customer record(s)' % len(customers))
    except Exception as e:
        # TODO don't fail for a single bad formatted customer, e.g. ""
        print('error: unable to load SQLite database: %s' % e)
    finally:
        if conn:
            conn.commit()
            conn.close()
