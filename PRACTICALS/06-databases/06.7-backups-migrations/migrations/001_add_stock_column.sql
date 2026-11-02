-- Migration 001: add stock column to products
-- UP: add the column
ALTER TABLE products ADD COLUMN stock INTEGER NOT NULL DEFAULT 0;

-- BACKFILL: existing rows get a sensible default
UPDATE products SET stock = 10 WHERE stock = 0;
