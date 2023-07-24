INSERT INTO users (userid, name, email, admin)
SELECT :userid, :name, :email, 1
WHERE NOT EXISTS(
        SELECT 1 FROM users WHERE userid = :userid
    )

