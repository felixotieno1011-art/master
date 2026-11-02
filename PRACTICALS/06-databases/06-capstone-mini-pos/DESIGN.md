# Mini Pos-Lab — Design

## 1. The 3 tables and what each stores
- customers: The unique people who buy things (id, name, phone).
- orders: The receipt/receipt header. Who bought it, and when (id, customer_id, date).
- order_items: The items inside the receipt. What they bought, how many, and the price at that exact moment (id, order_id, item_name, quantity, price).

## 2. Keys
- customers PK: `id`
- orders PK: `id`, FK to customers: `customer_id`
- order_items PK: `id`, FK to orders: `order_id`, FK to ___(what?) ___ 
  *(Answer: We do NOT need a `product_id` yet. Storing `item_name` and `price` directly in `order_items` is called "denormalization for history." If Mama Njeri changes the price of a mandazi tomorrow, the old receipts must still show KSh 15. So we snapshot the name and price inside the order_items).*

## 3. Relationships
- 1 customer → **Many** orders (1:N)
- 1 order → **Many** items (1:N)
- order_item → which product? (We use `item_name` and `price` to freeze the history. A separate `products` table can be added later for inventory management, but it's not strictly needed to answer her questions).

## 4. Which questions will this answer?
- "Who spent the most?" → `SELECT customers.name, SUM(order_items.quantity * order_items.price) AS total_spent FROM customers JOIN orders ON customers.id = orders.customer_id JOIN order_items ON orders.id = order_items.order_id GROUP BY customers.name ORDER BY total_spent DESC;`
- "What sells most?" → `SELECT item_name, SUM(quantity) AS total_sold FROM order_items GROUP BY item_name ORDER BY total_sold DESC;`
- "Show me all Wanjiku's orders" → `SELECT orders.date, order_items.item_name, order_items.quantity FROM customers JOIN orders ON customers.id = orders.customer_id JOIN order_items ON orders.id = order_items.order_id WHERE customers.name = 'Wanjiku';`

## 5. What I'm NOT storing (deliberately)
- **Stock/Inventory:** Right now, we only care about what she *sold*, not how much is left on the shelf.
- **Payments:** We don't track if she paid by M-Pesa or cash. (Add later).
- **Suppliers:** We don't track where the mandazi came from. (Add later).
