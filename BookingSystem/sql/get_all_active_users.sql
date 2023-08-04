SELECT *
FROM `users`
WHERE `expires_at` > DATETIME('now', 'localtime')
   OR `admin` = 1