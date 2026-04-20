# How to use and start Postgres in Command Line

## Make sure Postgres binaries are in PATH
- echo 'export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

## Start Postgres
- brew services start postgresql@16

## Check if Started
- postgresql@16  started

## Connect to DB
- psql postgres

## Create Database
- createdb mydb

## Verify Tables Exist
- \dt

## How to DROP TABLE
- DROP TABLE customers CASCADE; (CASCADE means also drop anything that depends on this table)
- DROP TABLE customers RESTRICT; (safer and the opposite--stops if there's dependencies)
- DROP TABLE customers; (same thing as above)

## Alternate approach to Creating and Inserting Data
- Use a setup.sql
- Paste all CREATE + INSERT statements
- psql mydb -f setup.sql
- 

## Create 6 tables
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);


CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name TEXT NOT NULL,
    sku TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,
    unit_price NUMERIC(10,2) NOT NULL
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL REFERENCES customers(customer_id),
    order_date DATE NOT NULL,
    order_status TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
Possible statuses:
* placed
* paid
* processing
* blocked
* shipped
* cancelled

CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES orders(order_id),
    product_id INT NOT NULL REFERENCES products(product_id),
    quantity INT NOT NULL
);

CREATE TABLE inventory (
    inventory_id SERIAL PRIMARY KEY,
    product_id INT NOT NULL REFERENCES products(product_id),
    warehouse_id INT NOT NULL,
    available_quantity INT NOT NULL,
    reserved_quantity INT NOT NULL DEFAULT 0
);

CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES orders(order_id),
    payment_date DATE,
    amount NUMERIC(10,2) NOT NULL,
    payment_status TEXT NOT NULL,
    transaction_reference TEXT
);
Possible statuses:
* pending
* completed
* failed
* refunded

CREATE TABLE shipments (
    shipment_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES orders(order_id),
    shipment_status TEXT NOT NULL,
    shipped_at TIMESTAMP,
    tracking_number TEXT
);
Possible statuses:
* not_created
* pending
* packed
* shipped
* delayed


## Insert Data into Tables
INSERT INTO customers (first_name, last_name, email) VALUES
('Ava', 'Martinez', 'ava.martinez@example.com'),
('Noah', 'Kim', 'noah.kim@example.com'),
('Mia', 'Johnson', 'mia.johnson@example.com'),
('Liam', 'Patel', 'liam.patel@example.com'),
('Sophia', 'Brown', 'sophia.brown@example.com'),
('Ethan', 'Garcia', 'ethan.garcia@example.com');

INSERT INTO products (product_name, sku, category, unit_price) VALUES
('Trail Running Shoes', 'SHOE-TRAIL-001', 'Footwear', 140.00),
('Hydration Vest', 'VEST-HYDRO-012', 'Gear', 165.00),
('Merino Wool Socks', 'SOCK-MERINO-003', 'Apparel', 22.00),
('Headlamp Pro', 'LAMP-PRO-010', 'Electronics', 89.00),
('Soft Flask 500ml', 'FLASK-500-021', 'Gear', 18.00),
('Ultralight Rain Jacket', 'JACKET-RAIN-044', 'Apparel', 210.00);

INSERT INTO orders (customer_id, order_date, order_status) VALUES
(1, '2026-04-01', 'shipped'),
(2, '2026-04-02', 'blocked'),
(3, '2026-04-03', 'processing'),
(4, '2026-04-04', 'paid'),
(5, '2026-04-05', 'processing'),
(6, '2026-04-06', 'cancelled');

INSERT INTO order_items (order_id, product_id, quantity) VALUES
-- Order 1: Ava, should be shipped
(1, 1, 1),
(1, 3, 2),

-- Order 2: Noah, blocked because payment failed
(2, 2, 1),
(2, 5, 2),

-- Order 3: Mia, pending payment
(3, 4, 1),

-- Order 4: Liam, paid but inventory shortage
(4, 6, 2),

-- Order 5: Sophia, payment/inventory okay but shipment delayed
(5, 1, 1),
(5, 2, 1),

-- Order 6: Ethan, cancelled
(6, 3, 4);

INSERT INTO inventory (product_id, warehouse_id, available_quantity, reserved_quantity) VALUES
-- Trail Running Shoes
(1, 101, 10, 2),
(1, 102, 4, 1),

-- Hydration Vest
(2, 101, 5, 1),
(2, 102, 3, 0),

-- Merino Wool Socks
(3, 101, 50, 10),
(3, 102, 30, 5),

-- Headlamp Pro
(4, 101, 8, 2),

-- Soft Flask 500ml
(5, 101, 20, 4),

-- Ultralight Rain Jacket
-- intentionally low available-to-sell for shortage test
(6, 101, 1, 0);

INSERT INTO payments (order_id, payment_date, amount, payment_status, transaction_reference) VALUES
-- Order 1: completed
(1, '2026-04-01', 184.00, 'completed', 'TXN-ORDER-001'),

-- Order 2: failed
(2, '2026-04-02', 201.00, 'failed', 'TXN-ORDER-002'),

-- Order 3: pending
(3, '2026-04-03', 89.00, 'pending', 'TXN-ORDER-003'),

-- Order 4: completed, but inventory shortage blocks it
(4, '2026-04-04', 420.00, 'completed', 'TXN-ORDER-004'),

-- Order 5: completed, but shipment delayed
(5, '2026-04-05', 305.00, 'completed', 'TXN-ORDER-005'),

-- Order 6: refunded/cancelled
(6, '2026-04-06', 88.00, 'refunded', 'TXN-ORDER-006');

INSERT INTO shipments (order_id, shipment_status, shipped_at, tracking_number) VALUES
-- Order 1: shipped successfully
(1, 'shipped', '2026-04-02 14:30:00', 'TRACK-001'),

-- Order 5: shipment exists but delayed
(5, 'delayed', NULL, 'TRACK-005');

-- Notice:
-- Order 2 has no shipment because payment failed.
-- Order 3 has no shipment because payment is pending.
-- Order 4 has no shipment because inventory is insufficient.
-- Order 6 has no shipment because order was cancelled.

## Validation Query
SELECT * FROM customers;
SELECT * FROM products;
SELECT * FROM orders;
SELECT * FROM order_items;
SELECT * FROM inventory;
SELECT * FROM payments;
SELECT * FROM shipments;

## Example Queries
SELECT
    o.order_id,
    c.first_name,
    c.last_name,
    o.order_status,
    p.payment_status,
    s.shipment_status
FROM orders o
JOIN customers c
    ON o.customer_id = c.customer_id
LEFT JOIN payments p
    ON o.order_id = p.order_id
LEFT JOIN shipments s
    ON o.order_id = s.order_id
ORDER BY o.order_id;

WITH latest_payment AS (
    SELECT
        p.payment_id,
        p.order_id,
        p.payment_date,
        p.amount,
        p.payment_status,
        p.transaction_reference,
        ROW_NUMBER() OVER (
            PARTITION BY p.order_id
            ORDER BY p.payment_date DESC NULLS LAST, p.payment_id DESC
        ) AS rn
    FROM payments p
),

latest_shipment AS (
    SELECT
        s.shipment_id,
        s.order_id,
        s.shipment_status,
        s.shipped_at,
        s.tracking_number,
        ROW_NUMBER() OVER (
            PARTITION BY s.order_id
            ORDER BY s.shipped_at DESC NULLS LAST, s.shipment_id DESC
        ) AS rn
    FROM shipments s
),

item_inventory AS (
    SELECT
        oi.order_id,
        oi.order_item_id,
        oi.product_id,
        pr.product_name,
        pr.sku,
        pr.category,
        oi.quantity AS ordered_quantity,
        COALESCE(SUM(i.available_quantity), 0) AS total_available_quantity,
        COALESCE(SUM(i.reserved_quantity), 0) AS total_reserved_quantity,
        COALESCE(SUM(i.available_quantity - i.reserved_quantity), 0) AS available_to_sell,
        GREATEST(
            oi.quantity - COALESCE(SUM(i.available_quantity - i.reserved_quantity), 0),
            0
        ) AS shortage_quantity,
        (COALESCE(SUM(i.available_quantity - i.reserved_quantity), 0) >= oi.quantity) AS item_can_fulfill
    FROM order_items oi
    JOIN products pr
        ON oi.product_id = pr.product_id
    LEFT JOIN inventory i
        ON oi.product_id = i.product_id
    GROUP BY
        oi.order_id,
        oi.order_item_id,
        oi.product_id,
        pr.product_name,
        pr.sku,
        pr.category,
        oi.quantity
),

order_inventory_summary AS (
    SELECT
        order_id,
        COUNT(*) AS item_count,
        SUM(ordered_quantity) AS total_units_ordered,
        BOOL_AND(item_can_fulfill) AS all_items_available,
        COUNT(*) FILTER (WHERE item_can_fulfill = FALSE) AS short_item_count,
        SUM(shortage_quantity) AS total_short_units,
        STRING_AGG(
            CASE
                WHEN item_can_fulfill = FALSE THEN
                    product_name
                    || ' [' || sku || '] short by '
                    || shortage_quantity::TEXT
                    || ' units'
                ELSE NULL
            END,
            '; '
            ORDER BY product_name
        ) AS shortage_detail
    FROM item_inventory
    GROUP BY order_id
),

order_value AS (
    SELECT
        oi.order_id,
        SUM(oi.quantity * pr.unit_price) AS expected_order_total
    FROM order_items oi
    JOIN products pr
        ON oi.product_id = pr.product_id
    GROUP BY oi.order_id
),

fulfillment_base AS (
    SELECT
        o.order_id,
        o.order_date,
        o.order_status,
        c.customer_id,
        c.first_name,
        c.last_name,
        c.email,

        ov.expected_order_total,

        lp.payment_id,
        lp.payment_date,
        lp.amount AS latest_payment_amount,
        lp.payment_status,
        lp.transaction_reference,

        ois.item_count,
        ois.total_units_ordered,
        ois.all_items_available,
        ois.short_item_count,
        ois.total_short_units,
        ois.shortage_detail,

        ls.shipment_id,
        ls.shipment_status,
        ls.shipped_at,
        ls.tracking_number
    FROM orders o
    JOIN customers c
        ON o.customer_id = c.customer_id
    LEFT JOIN order_value ov
        ON o.order_id = ov.order_id
    LEFT JOIN latest_payment lp
        ON o.order_id = lp.order_id
       AND lp.rn = 1
    LEFT JOIN order_inventory_summary ois
        ON o.order_id = ois.order_id
    LEFT JOIN latest_shipment ls
        ON o.order_id = ls.order_id
       AND ls.rn = 1
)

SELECT
    order_id,
    customer_id,
    first_name,
    last_name,
    email,
    order_date,
    order_status,

    expected_order_total,
    latest_payment_amount,
    payment_status,
    payment_date,
    transaction_reference,

    item_count,
    total_units_ordered,
    all_items_available,
    short_item_count,
    total_short_units,
    shortage_detail,

    shipment_status,
    shipped_at,
    tracking_number,

    CASE
        WHEN order_status = 'cancelled'
            THEN 'cancelled'

        WHEN payment_status IS NULL
            THEN 'payment_missing'

        WHEN payment_status = 'failed'
            THEN 'payment_failed'

        WHEN payment_status = 'pending'
            THEN 'payment_pending'

        WHEN payment_status = 'refunded'
            THEN 'payment_refunded'

        WHEN COALESCE(all_items_available, FALSE) = FALSE
            THEN 'inventory_blocked'

        WHEN shipment_id IS NULL
            THEN 'shipment_not_created'

        WHEN shipment_status = 'delayed'
            THEN 'shipment_delayed'

        WHEN shipment_status = 'shipped'
            THEN 'shipped'

        ELSE 'needs_investigation'
    END AS fulfillment_state,

    CASE
        WHEN order_status = 'cancelled'
            THEN 'Order was cancelled; no fulfillment action should proceed.'

        WHEN payment_status IS NULL
            THEN 'No payment attempt exists for this order.'

        WHEN payment_status = 'failed'
            THEN 'Latest payment failed; order should not ship until payment succeeds.'

        WHEN payment_status = 'pending'
            THEN 'Payment is still pending; wait for completion before fulfillment.'

        WHEN payment_status = 'refunded'
            THEN 'Payment was refunded; order should not ship.'

        WHEN COALESCE(all_items_available, FALSE) = FALSE
            THEN 'Inventory shortage prevents shipment: ' || COALESCE(shortage_detail, 'unknown item shortage')

        WHEN shipment_id IS NULL
            THEN 'Payment and inventory are acceptable, but no shipment has been created.'

        WHEN shipment_status = 'delayed'
            THEN 'Shipment exists but is delayed; check warehouse/carrier handling.'

        WHEN shipment_status = 'shipped'
            THEN 'Order has shipped with tracking number ' || COALESCE(tracking_number, 'unknown')

        ELSE 'Workflow state is unclear and needs manual investigation.'
    END AS business_explanation,

    CASE
        WHEN order_status = 'cancelled'
            THEN 'No action: cancelled order.'

        WHEN payment_status IS NULL
            THEN 'Create or locate payment attempt.'

        WHEN payment_status = 'failed'
            THEN 'Contact customer or retry payment.'

        WHEN payment_status = 'pending'
            THEN 'Wait for payment settlement.'

        WHEN payment_status = 'refunded'
            THEN 'Confirm cancellation/refund handling.'

        WHEN COALESCE(all_items_available, FALSE) = FALSE
            THEN 'Replenish inventory or split/backorder shipment.'

        WHEN shipment_id IS NULL
            THEN 'Create shipment.'

        WHEN shipment_status = 'delayed'
            THEN 'Investigate warehouse delay or carrier issue.'

        WHEN shipment_status = 'shipped'
            THEN 'No action required.'

        ELSE 'Escalate for manual review.'
    END AS recommended_next_action

FROM fulfillment_base
ORDER BY
    CASE
        WHEN order_status = 'cancelled' THEN 9
        WHEN payment_status IS NULL THEN 1
        WHEN payment_status = 'failed' THEN 2
        WHEN payment_status = 'pending' THEN 3
        WHEN payment_status = 'refunded' THEN 4
        WHEN COALESCE(all_items_available, FALSE) = FALSE THEN 5
        WHEN shipment_id IS NULL THEN 6
        WHEN shipment_status = 'delayed' THEN 7
        WHEN shipment_status = 'shipped' THEN 8
        ELSE 10
    END,
    order_id;


## How to update
Ex #1: Update multiple columns
UPDATE table_name
SET column1 = value1,
    column2 = value2
WHERE condition;

Ex #2: Update one order’s status
UPDATE orders
SET order_status = 'processing',
    created_at = NOW()
WHERE order_id = 4;

Ex #3: Be careful leaving off WHERE
UPDATE orders
SET order_status = 'processing';

Ex #4: Use RETURNING to see what changed
UPDATE payments
SET payment_status = 'completed',
    payment_date = CURRENT_DATE
WHERE order_id = 3
RETURNING *;

Ex #5: Update a shipment to shipped
UPDATE shipments
SET shipment_status = 'shipped',
    shipped_at = NOW(),
    tracking_number = 'TRACK-005-COMPLETE'
WHERE order_id = 5
RETURNING *;

Ex #6: Update inventory after restocking
UPDATE inventory
SET available_quantity = available_quantity + 10
WHERE product_id = 6
RETURNING *;

## Data Model Explanation
The model represents a basic ecommerce fulfillment system:

A customer places an order.
The order contains products.
The products require inventory.
The order needs payment.
If payment and inventory are okay, shipment can happen.

Tables:
customers - Stores who placed the order.
customers
---------
customer_id
first_name
last_name
email
created_at
One customer can have many orders.

products - stores what can be purchased
products
--------
product_id
product_name
sku
category
unit_price
Products are referenced by order_items and inventory.

orders - stores the main order record.
orders
------
order_id
customer_id
order_date
order_status
created_at
Each order belongs to one customer.
Example statuses: 
placed
paid
processing
blocked
shipped
cancelled

order_items - stores the individual products inside the order
order_items
-----------
order_item_id
order_id
product_id
quantity
This is the bridge between orders and products.
One order can have many order items.

inventory - stores available stock by product and warehouse.
inventory
---------
inventory_id
product_id
warehouse_id
available_quantity
reserved_quantity
This tells whether a product can actually be fulfilled.
important calculation - available_to_sell = available_quantity - reserved_quantity

payments - stores payment attempts for an order
payments
--------
payment_id
order_id
payment_date
amount
payment_status
transaction_reference
One order can have multiple payment attempts.
Example statuses: 
pending
completed
failed
refunded

shipments - stores shipment records for an order.
shipments
---------
shipment_id
order_id
shipment_status
shipped_at
tracking_number
An order may or may not have a shipment yet.
Example statuses:
pending
packed
shipped
delayed

Data Model Flow: 
customers
   |
   | customer_id
   v
orders
   |
   | order_id
   +--------------------+
   |                    |
   v                    v
order_items          payments
   |
   | product_id
   v
products
   |
   | product_id
   v
inventory

orders
   |
   | order_id
   v
shipments

Compact Version: 
customers → orders → order_items → products → inventory
                 |
                 ├── payments
                 |
                 └── shipments
                 
Business Flow Graph: 
Customer places order
        |
        v
Order created
        |
        v
Check payment
        |
        +--> payment failed     → block order
        |
        +--> payment pending    → wait for payment
        |
        +--> payment completed  → continue
                                  |
                                  v
                           Check inventory
                                  |
                                  +--> insufficient stock → block/backorder
                                  |
                                  +--> enough stock       → continue
                                                            |
                                                            v
                                                     Check shipment
                                                            |
                                                            +--> no shipment       → create shipment
                                                            |
                                                            +--> shipment delayed  → investigate delay
                                                            |
                                                            +--> shipped           → complete         

1. Get each order
2. Attach the customer
3. Find the latest payment
4. Calculate inventory availability for every item
5. Collapse item inventory into order-level inventory status
6. Find the latest shipment
7. Decide the fulfillment state
8. Give a business explanation
9. Recommend next action

Potential Pack Order
Step 1: Ecommerce Order Fulfillment
Step 2: Order Status Flow
Step 3: Payment Check
Step 4: Inventory Availability Check
Step 5: Available To Sell Calculation
Step 6: Shipment Check
Step 7: Fulfillment Explanation Rules