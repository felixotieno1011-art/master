-- Q1: Who spent the most?
-- This joins all 3 tables, multiplies quantity × price for each item,
-- and sums it up per customer. Then sorts highest to lowest.
SELECT
    c.name,
    SUM(oi.quantity * oi.unit_price) AS total_spent
FROM customers c
JOIN orders o       ON o.customer_id = c.id
JOIN order_items oi ON oi.order_id   = o.id
GROUP BY c.name
ORDER BY total_spent DESC;


-- Q2: What sells most?
-- This groups by item name and adds up all quantities sold.
SELECT
    item_name,
    SUM(quantity) AS total_sold
FROM order_items
GROUP BY item_name
ORDER BY total_sold DESC;


-- Q3: Show me all of Wanjiku's orders
-- Filter to one customer, then show the date and items she bought.
SELECT
    o.created_at AS date,
    oi.item_name,
    oi.quantity,
    oi.unit_price,
    (oi.quantity * oi.unit_price) AS line_total
FROM customers c
JOIN orders o       ON o.customer_id = c.id
JOIN order_items oi ON oi.order_id   = o.id
WHERE c.name = 'Wanjiku'
ORDER BY o.created_at;
