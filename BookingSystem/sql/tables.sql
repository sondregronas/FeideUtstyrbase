CREATE TABLE IF NOT EXISTS `inventory`
(
    `id`                 TEXT PRIMARY KEY NOT NULL,
    `name`               TEXT             NOT NULL,
    `category`           TEXT             NOT NULL,
    `included_batteries` INTEGER          NOT NULL DEFAULT 0,
    `available`          INTEGER          NOT NULL DEFAULT 1,
    `active_order`       TEXT,
    `order_due_date`     TEXT,
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