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

-- SELECT DISTINCT order identifiers
SELECT distinct(o_order_id) FROM orders;
