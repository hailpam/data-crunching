import requests
import json
import time
import argparse
import locale

from datetime import datetime

BASE_URL = 'https://www.gestionalesmarty.com/titanium'
API_URI = 'V2/Api/Sales_Orders'
METHOD = 'list'


class Item:
    '''
        Order Item. It enlists relevant attributes related to the specific item of the
        given order.
    '''
    def __init__(self, product_id, sku, name, price, discount, tax_id, tax, qty):
        self.product_id = product_id
        self.sku = sku
        self.name = name
        self.price = locale.format('%f', float(price))
        self.discount = locale.format('%f', float(discount))
        self.tax_id = locale.format('%f', float(tax_id))
        self.tax = locale.format('%f', float(tax))
        self.qty = locale.format('%f', float(qty))
    
    def to_header(self):
        '''
            Header columns formatting string.
        '''
        return '%s,%s,%s,%s,%s,%s,%s,%s' % ('i.product_id', 'i.sku', 'i.name', 'i.price', 'i.discount', 'i.tax_id', 'i.tax', 'i.qty')

    def to_csv(self):
        '''
            Export to CSV the deserialized version of the data.
        '''
        return '\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\"' % (self.product_id, self.sku, self.name, self.price, self.discount, self.tax_id, self.tax, self.qty)

    def __str__(self):
        return '%s, %s, %s, %s, %s, %s, %s, %s' % (self.product_id, self.sku, self.name, self.price, self.discount, self.tax_id, self.tax, self.qty)

class Customer:
    '''
        Customer Item. It enlists relevant attributes related to the customr submitting
        a given order.
    '''
    def __init__(self, name, address, zipcode, city, state, country_iso):
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.city = city
        self.state = state
        self.country_iso = country_iso
    
    def to_header(self):
        '''
            Header columns formatting string.
        '''
        return '%s,%s,%s,%s,%s,%s' % ('c.name', 'c.address', 'c.zipcode', 'c.city', 'c.state', 'c.country_iso')

    def to_csv(self):
        '''
            Export to CSV the deserialized version of the data.
        '''
        return '\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\"' % (self.name, self.address, self.zipcode, self.city, self.state, self.country_iso)

    def __str__(self):
        return '%s, %s, %s, %s, %s, %s' % (self.name, self.address, self.zipcode, self.city, self.state, self.country_iso)

class Shipment:
    '''
        Shipment info. It enlists relevant attributes related to the shipment as well as to the carrier.
    '''
    def __init__(self, weight, date, carrier, shipped, shipping_confirmed, fees_shipping, fees_payment, fees_extra, locked):
        self.weight = weight if weight else 'No weight'
        self.date = date if date else 'No date'
        self.carrier = carrier if carrier else 'No carrier'
        self.shipped = shipped if shipped else 'No shipped'
        self.shipping_confirmed = locale.format('%f', float(shipping_confirmed)) if shipping_confirmed else 'No shipping'
        self.fees_shipping = locale.format('%f', float(fees_shipping)) if fees_shipping else 'No fees shipping'
        self.fees_payment = locale.format('%f', float(fees_payment)) if fees_payment else 'No fees payment'
        self.fees_extra = locale.format('%f', float(fees_extra)) if fees_extra else 'No fees extra'
        self.locked = locale.format('%f', float(locked)) if locked else 'No locked'

    def to_header(self):
        '''
            Header columns formatting string.
        '''
        return '%s,%s,%s,%s,%s,%s,%s,%s,%s' % ('s.weight', 's.date', 's.carrier', 's.shipped', 's.shipping_confirmed', 's.fees_shipping', 's.fees_payment', 's.fees_extra', 's.locked')

    def to_csv(self):
        '''
            Export to CSV the deserialized version of the data.
        '''
        return '\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\"' % (self.weight, self.date, self.carrier, self.shipped, self.shipping_confirmed, self.fees_shipping, self.fees_payment, self.fees_extra, self.locked)

    def __str__(self):
        return '%s, %s, %s, %s, %s, %s, %s, %s, %s' % (self.weight, self.date, self.carrier, self.shipped, self.shipping_confirmed, self.fees_shipping, self.fees_payment, self.fees_extra, self.locked)

class Order:
    '''
        Order item. It enlists relevant attributes related to the order itself.
    '''
    def __init__(self, order_id, date, number, code, payment_type, customer, shipment):
        self.id = order_id
        self.date = date
        self.number = number
        self.code = code
        self.payment_type = payment_type
        self.customer = customer
        self.items = []
        self.shipment = shipment
    
    def to_header(self):
        '''
            Header columns formatting string.
        '''
        return '%s,%s,%s,%s,%s' % ('o.order_id', 'o.date', 'o.number', 'o.code', 'o.payment_type')

    def to_csv(self):
        '''
            Export to CSV the deserialized version of the data.
        '''
        return '\"%s\",\"%s\",\"%s\",\"%s\",\"%s\"' % (self.id, self.date, self.number, self.code, self.payment_type)

    def __str__(self):
        s = '%s, %s, %s, %s, %s, %s\n' % (self.id, self.date, self.number, self.code, self.payment_type, self.customer)
        s += '\t%s\n' % self.customer
        s += '\t%s\n' % self.shipment
        for item in self.items:
            s += '\t\t%s\n' % item
        return s

def load_data(api_key):
    '''
        Load the data up. It transforms it into an internal format which is then re-used for export.
    '''
    loaded_orders = []
    
    res = requests.get('%s/%s/%s?ApiKey=%s' % (BASE_URL, API_URI, METHOD, api_key))
    orders = json.loads(res.text)
    if res.status_code != 200 or 'error' in res.text:
        print('error: not able to fetch data: %s' % res.text)
        raise Exception(res.text)
    
    for order in orders:
        c = Customer(order['billing_address']['name'], order['billing_address']['address'], order['billing_address']['zipcode'], order['billing_address']['city'], order['billing_address']['state'], order['billing_address']['country_iso'])
        s = Shipment(order['weight'], order['shipping_date'], order['carrier'], order['shipped'], order['shipping_confirmed'], order['fees']['shipping'], order['fees']['payment'], order['fees']['extra'], order['locked'])
        o = Order(order['id'], order['date'], order['number'], order['code'], order['payment_type'], c, s)
        rows = order['rows']
        for row in rows:
            i = Item(row['id'], row['sku'], row['name'], row['price'], row['discount'], row['tax_id'], row['tax'], row['quantity'])
            o.items.append(i)
        loaded_orders.append(o)
    
    return loaded_orders

def export_to_csv(orders):
    '''
        Export the internal deserialized version of the data into a CSV file. The CSV file can be then reused with Excel or compatible
        programs to create pivot tables and so analytics.
    '''
    try:
        now = datetime.now()
        f = open(now.strftime('%Y%m%d_%H%M%S_export.csv'), 'w')
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

def export_to_dsv(orders):
    pass

def parse_arguments():
    '''
        Parse input arguments. Passing the API key is defined as mandatory.
    '''
    parser = argparse.ArgumentParser(description='Exports JSON orders data into CSV format.')
    parser.add_argument('-k', '--key', type=str, required=True, help='API key to be used to perform the REST request to the backend')
    parser.add_argument('-l', '--locale', type=str, required=False, help='Specify the locale: it_IT for italian')
    args = parser.parse_args()
    
    return args

def main():
    args = parse_arguments()
    if args.locale:
        locale.setlocale(locale.LC_ALL, args.locale)
    orders = load_data(args.key)
    print('info: loaded orders...')
    for order in orders:
        print(order)
    export_to_csv(orders)
    print('info: export successul')

if __name__ == "__main__":
    main()
