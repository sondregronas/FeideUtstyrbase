REPLACE INTO users
(userid, name, classroom, classroom_teacher, email, personal_email, updated_at, expires_at, ban_reason, last_booked_at,
 active_orders, affiliations)
VALUES (:userid, :name, :classroom, :classroom_teacher, :email, :personal_email, :updated_at, :expires_at, :ban_reason,
        :last_booked_at, :active_orders, :affiliations)