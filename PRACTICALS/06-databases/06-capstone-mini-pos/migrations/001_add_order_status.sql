-- Migration 001: add status column to orders
-- UP
ALTER TABLE orders ADD COLUMN status TEXT NOT NULL DEFAULT 'pending';

-- BACKFILL: all existing orders are treated as already paid
UPDATE orders SET status = 'paid' WHERE status = 'pending';

-- Add a CHECK constraint (via table rebuild, or just document the allowed values)
