SELECT *
FROM inventory
WHERE available = 0
  AND order_due_date > DATETIME('now')