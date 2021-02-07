import locale

from util import *

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
    def __init__(self, name, address, zipcode, city, state, country_iso, email=None, identifier=None, phone=None, business_name=None, created_at=None, updated_at=None, vat=None):
        self.id = int(identifier)
        self.name = name_to_camelcase(name) if name else name
        self.address = name_to_camelcase(address).replace('"', '\'') if address else address.replace('"', '\'')
        self.zipcode = zipcode
        self.city = name_to_camelcase(city) if city else city
        self.state = state.upper() if state else state
        self.country_iso = country_iso.upper() if country_iso else country_iso
        self.email = email.lower() if email else 'No email'
        self.phone = phone if phone else 'No phone'
        self.business_name = name_to_camelcase(business_name) if business_name else 'No business name'
        self.created_at = created_at if created_at else 'No creation date'
        self.updated_at = updated_at if updated_at else 'No update date'
        self.vat = vat if vat else 'No VAT'
    
    def to_header(self):
        '''
            Header columns formatting string.
        '''
        return '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ('c.name', 'c.id', 'c.address', 'c.zipcode', 'c.city', 'c.state', 'c.country_iso', 'c.email', 'c.phone', 'c.business_name','c.created_at','c.updated_at','c.vat')

    def to_csv(self):
        '''
            Export to CSV the deserialized version of the data.
        '''
        return '\"%s\",\"%d\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\"' % (self.name, self.id, self.address, self.zipcode, self.city, self.state, self.country_iso, self.email, self.phone, self.business_name, self.created_at, self.updated_at, self.vat)

    def __str__(self):
        return '%s, %d, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s' % (self.name, self.id, self.address, self.zipcode, self.city, self.state, self.country_iso, self.email, self.phone, self.business_name, self.created_at, self.updated_at, self.vat)

class Shipment:
    '''
        Shipment info. It enlists relevant attributes related to the shipment as well as to the carrier.
    '''
    def __init__(self, weight, date, carrier, shipped, shipping_confirmed, fees_shipping, fees_payment, fees_extra, locked, shipping_canceled=None, shipping_locked=None):
        self.weight = weight if weight else 'No weight'
        self.date = date if date else 'No date'
        self.carrier = carrier if carrier else 'No carrier'
        self.shipped = shipped if shipped else 'No shipped'
        self.shipping_confirmed = locale.format('%f', float(shipping_confirmed)) if shipping_confirmed else 'No shipping'
        self.shipping_canceled = shipping_canceled if shipping_canceled else 'No shipping canceled'
        self.shipping_locked = shipping_locked if shipping_locked else 'No shipping locked'
        self.fees_shipping = locale.format('%f', float(fees_shipping)) if fees_shipping else 'No fees shipping'
        self.fees_payment = locale.format('%f', float(fees_payment)) if fees_payment else 'No fees payment'
        self.fees_extra = locale.format('%f', float(fees_extra)) if fees_extra else 'No fees extra'
        self.locked = locale.format('%f', float(locked)) if locked else 'No locked'

    def to_header(self):
        '''
            Header columns formatting string.
        '''
        return '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ('s.weight', 's.date', 's.carrier', 's.shipped', 's.shipping_confirmed', 's.shipping_canceled', 's.shipping_locked', 's.fees_shipping', 's.fees_payment', 's.fees_extra', 's.locked')

    def to_csv(self):
        '''
            Export to CSV the deserialized version of the data.
        '''
        return '\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\"' % (self.weight, self.date, self.carrier, self.shipped, self.shipping_confirmed, self.shipping_canceled, self.shipping_locked, self.fees_shipping, self.fees_payment, self.fees_extra, self.locked)

    def __str__(self):
        return '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s' % (self.weight, self.date, self.carrier, self.shipped, self.shipping_confirmed, self.shipping_canceled, self.shipping_locked, self.fees_shipping, self.fees_payment, self.fees_extra, self.locked)

class Order:
    '''
        Order item. It enlists relevant attributes related to the order itself.
    '''
    def __init__(self, order_id, date, number, code, payment_type, customer, shipment, paid=None, cod_value=None, nr_packages=None, nr_payments=None):
        self.id = int(order_id)
        self.date = date.split('T')[0]
        self.time = date.split('T')[1]
        self.number = number
        self.code = code
        self.payment_type = payment_type
        self.customer = customer
        self.items = []
        self.shipment = shipment
        self.paid = paid if paid else 'No paid'
        self.cod_value = cod_value if cod_value else 'No code value'
        self.nr_packages = len(nr_packages) if nr_packages else 0
        self.nr_payments = len(nr_payments) if nr_payments else 0
    
    def to_header(self):
        '''
            Header columns formatting string.
        '''
        return '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ('o.order_id', 'o.date', 'o.time', 'o.number', 'o.code', 'o.payment_type', 'o.paid', 'o.code_value', 'o.nr_packages', 'o.nr_payments')

    def to_csv(self):
        '''
            Export to CSV the deserialized version of the data.
        '''
        return '\"%d\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%d\",\"%d\"' % (self.id, self.date, self.time, self.number, self.code, self.payment_type, self.paid, self.cod_value, self.nr_packages, self.nr_payments)

    def __str__(self):
        s = '%d, %s, %s, %s, %s, %s, %s, %s, %d, %d, %s\n' % (self.id, self.date, self.time, self.number, self.code, self.payment_type, self.paid, self.cod_value, self.nr_packages, self.nr_payments, self.customer)
        s += '\t%s\n' % self.customer
        s += '\t%s\n' % self.shipment
        for item in self.items:
            s += '\t\t%s\n' % item
        return s
