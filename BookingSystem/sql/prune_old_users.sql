DELETE
FROM users
WHERE expires_at < DATETIME('now', 'localtime')
  AND admin = 0;