-- ============================================================
-- Seed data for Mama Njeri's Mini POS
-- ============================================================

-- 1. CUSTOMERS (3)
INSERT INTO customers (name, phone) VALUES
  ('Wanjiku', '0711000001'),
  ('Otieno',  '0722000002'),
  ('Amina',   '0733000003');

-- 2. ORDERS (5)
INSERT INTO orders (customer_id, created_at) VALUES
  (1, '2026-11-02 09:00:00'),  -- Wanjiku, Monday morning
  (1, '2026-11-02 14:30:00'),  -- Wanjiku, Monday afternoon
  (2, '2026-11-03 10:15:00'),  -- Otieno, Tuesday
  (1, '2026-11-03 12:00:00'),  -- Wanjiku, Tuesday (her 3rd order!)
  (3, '2026-11-04 08:45:00');  -- Amina, Wednesday morning

-- 3. ORDER ITEMS (10 total)
INSERT INTO order_items (order_id, item_name, quantity, unit_price) VALUES
  (1, 'Mandazi', 3, 15),   -- Wanjiku Mon: 3 mandazi = 45
  (1, 'Soda',    1, 50),   -- Wanjiku Mon: 1 soda = 50
  (2, 'Bread',   2, 60),   -- Wanjiku Mon PM: 2 bread = 120
  (3, 'Bread',   2, 60),   -- Otieno Tue: 2 bread = 120
  (3, 'Soda',    1, 50),   -- Otieno Tue: 1 soda = 50
  (4, 'Mandazi', 5, 15),   -- Wanjiku Tue: 5 mandazi = 75
  (4, 'Soda',    2, 50),   -- Wanjiku Tue: 2 soda = 100
  (5, 'Mandazi', 4, 15),   -- Amina Wed: 4 mandazi = 60
  (5, 'Bread',   1, 60),   -- Amina Wed: 1 bread = 60
  (5, 'Soda',    1, 50);   -- Amina Wed: 1 soda = 50
