CREATE TABLE IF NOT EXISTS `inventory`
(
    `id`                 TEXT PRIMARY KEY NOT NULL,
    `name`               TEXT             NOT NULL,
    `category`           TEXT             NOT NULL,
    `included_batteries` INTEGER          NOT NULL DEFAULT 0,
    `available`          INTEGER          NOT NULL DEFAULT 1,
    `borrowed_to`        TEXT,
    `order_due_date`     TEXT,
    `last_seen`          TEXT,
    UNIQUE (`id`)
);

CREATE TABLE IF NOT EXISTS `users`
(
    `id`         INTEGER PRIMARY KEY AUTOINCREMENT,
    `userid`     TEXT    NOT NULL,
    `name`       TEXT    NOT NULL,
    `classroom`  TEXT,
    `email`      TEXT    NOT NULL,
    `updated_at` TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `expires_at` TEXT,
    `admin`      INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (`classroom`) REFERENCES `groups` (`classroom`),
    UNIQUE (`userid`)
);

CREATE TABLE IF NOT EXISTS `groups`
(
    `id`        INTEGER PRIMARY KEY AUTOINCREMENT,
    `classroom` TEXT NOT NULL,
    UNIQUE (`classroom`)
);

CREATE TABLE IF NOT EXISTS `categories`
(
    `id`   INTEGER PRIMARY KEY AUTOINCREMENT,
    `name` TEXT NOT NULL,
    UNIQUE (`name`)
);


INSERT INTO `categories` (`name`)
SELECT t.*
FROM (VALUES ('Kamera'),
             ('Objektiv'),
             ('Batteri'),
             ('Lader'),
             ('Minnekort'),
             ('Minnekortleser'),
             ('Lys'),
             ('Mikrofon'),
             ('Stativ'),
             ('Filter'),
             ('Lydopptaker'),
             ('Adapter'),
             ('PC'),
             ('Skjerm'),
             ('Gimbal'),
             ('Drone'),
             ('Tegnebrett'),
             ('Lagringsenhet'),
             ('Headset'),
             ('Kabel'),
             ('Nettverk'),
             ('Diverse'),
             ('Mangler kategori')) t
WHERE NOT EXISTS(SELECT * FROM `categories`);

CREATE TABLE IF NOT EXISTS `audits`
(
    `id`        INTEGER PRIMARY KEY AUTOINCREMENT,
    `timestamp` TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `event`     TEXT NOT NULL,
    `message`   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS `settings`
(
    `id`    INTEGER PRIMARY KEY AUTOINCREMENT,
    `name`  TEXT NOT NULL,
    `value` TEXT NOT NULL,
    UNIQUE (`name`)
);