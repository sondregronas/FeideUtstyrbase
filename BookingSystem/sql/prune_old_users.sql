DELETE
FROM users
WHERE expires_at < datetime("now")
  AND admin = 0;