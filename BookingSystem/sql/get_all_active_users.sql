SELECT *
FROM `users`
WHERE `expires_at` > DATETIME('now')
   OR `admin` = 1