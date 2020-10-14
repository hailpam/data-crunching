-- DROP TABLE orders
DROP TABLE orders;

-- CREATE TABLE orders
CREATE TABLE orders (
    o_order_id text,
    o_date text,
    o_time text,
    o_number text,
    o_code text,
    o_payment_type text,
    c_name text,
    c_address text,
    c_zipcode text,
    c_city text,
    c_state text,
    c_country_iso text,
    c_id text,
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

-- UPDATE row
UPDATE orders
SET o_date = "%s",
    o_time = "%s",
    o_number = "%s",
    o_code = "%s",
    o_payment_type = "%s",
    c_name = "%s",
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

-- SELECT DISTINCT order identifiers
SELECT distinct(o_order_id) FROM orders;

-- SELECT queries
SELECT o_order_id, 
    c_name, 
    SUM(i_price) AS "spent", 
    SUM(i_qty) AS "items"
FROM orders
GROUP BY o_order_id, c_name;
