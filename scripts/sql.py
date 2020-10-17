
SQL_DROP_TABLE = 'DROP TABLE orders;'

SQL_CREATE_TABLE = """
CREATE TABLE orders (
    o_order_id text,
    o_date text,
    o_time text,
    o_number text,
    o_code text,
    o_payment_type text,
    c_name text,
    c_id text,
    c_address text,
    c_zipcode text,
    c_city text,
    c_state text,
    c_country_iso text,
    i_product_id text,
    i_sku text,
    i_name text,
    i_price text,
    i_discount text,
    i_tax_id text,
    i_tax text,
    i_qty text,
    s_weight text,
    s_date text,
    s_carrier text,
    s_shipped text,
    s_shipping_confirmed text,
    s_fees_shipping text,
    s_fees_payment text,
    s_fees_extra text,
    s_locked text
);
"""

SQL_INSERT = 'INSERT INTO orders VALUES (%s,%s,%s,%s)'

SQL_UPDATE = """
UPDATE orders
SET o_date = "%s",
    o_time = "%s",
    o_number = "%s",
    o_code = "%s",
    o_payment_type = "%s",
    c_name = "%s",
    c_id = "%s",
    c_address = "%s",
    c_zipcode = "%s",
    c_city = "%s",
    c_state = "%s",
    c_country_iso = "%s",
    i_product_id = "%s",
    i_sku = "%s",
    i_name = "%s",
    i_price = "%s",
    i_discount = "%s",
    i_tax_id = "%s",
    i_tax = "%s",
    i_qty = "%s",
    s_weight = "%s",
    s_date = "%s",
    s_carrier = "%s",
    s_shipped = "%s",
    s_shipping_confirmed = "%s",
    s_fees_shipping = "%s",
    s_fees_payment = "%s",
    s_fees_extra = "%s",
    s_locked = "%s"
WHERE
    o_order_id = "%s"
"""

SQL_DELETE = """
DELETE FROM orders
WHERE o_order_id = %d;
"""

SQL_SELECT_DISTINCT_ID = 'SELECT distinct(o_order_id) FROM orders'

def insert_record(order, item):
    return SQL_INSERT % (
        order.to_csv(), 
        order.customer.to_csv(), 
        item.to_csv(), 
        order.shipment.to_csv()
    )

def update_record(order, item):
    return SQL_UPDATE % (
        order.date,
        order.time,
        order.number,
        order.code,
        order.payment_type,
        order.customer.name,
        order.customer.id,
        order.customer.address,
        order.customer.zipcode,
        order.customer.city,
        order.customer.state,
        order.customer.country_iso,
        item.product_id,
        item.sku,
        item.name,
        item.price,
        item.discount,
        item.tax_id,
        item.tax,
        item.qty,
        order.shipment.weight,
        order.shipment.date,
        order.shipment.carrier,
        order.shipment.shipped,
        order.shipment.shipping_confirmed,
        order.shipment.fees_shipping,
        order.shipment.fees_payment,
        order.shipment.fees_extra,
        order.shipment.locked,
        order.id
    )

def delete_records(order):
    return SQL_DELETE % (
        order.id
    )
