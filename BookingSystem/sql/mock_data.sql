INSERT INTO `users` (`userid`, `name`, `email`, `admin`, `classroom`, `expires_at`)
VALUES ('0', 'Arne Underviser', '', 1, null, null),

       ('1', 'Kari Elev', '', 0, '1C (Arne Underviser)',
        DATETIME('now', '+1 year', 'localtime')),

       ('2', 'Ekstra Langt Navn Som Er Ekstra Langt', '', 0, '1B (Jens Underviser)',
        DATETIME('now', '+1 year', 'localtime')),

       ('3', 'Per Elevnavn', '', 0, '3C (Siri Underviser)',
        DATETIME('now', '+1 year', 'localtime')),

       ('4', 'Invalid User', '', 0, '2B (Pensjonert Underviser)',
        DATETIME('now', '-1 day', 'localtime'));

INSERT INTO `inventory` (`id`, `name`, `category`, `included_batteries`, `available`, `borrowed_to`, `order_due_date`,
                         `last_seen`)
VALUES ('Bee-Bot-01', 'Bee-Bot Den Nye Undervisningsrobotten', 'Robot', 4, 1, NULL, NULL,
        DATETIME('now', '-55 days', 'localtime')),

       ('Bee-Bot-02', 'Bee-Bot Den Nye Undervisningsrobotten', 'Robot', 4, 0, '0',
        DATETIME('now', '-1 day', 'localtime'),
        DATETIME('now', '-7 days', 'localtime')),

       ('Bee-Bot-03', 'Bee-Bot Den Nye Undervisningsrobotten', 'Robot', 4, 0, '0',
        DATETIME('now', '-7 days', 'localtime'),
        DATETIME('now', '-7 days', 'localtime')),

       ('Bee-Bot-04', 'Bee-Bot Den Nye Undervisningsrobotten', 'Robot', 4, 0, '1',
        DATETIME('now', '2 days', 'localtime'),
        DATETIME('now', 'localtime')),

       ('A6400-01', 'Sony A6400', 'Camera', 1, 0, '1',
        DATETIME('now', 'localtime'),
        DATETIME('now', 'localtime')),

       ('A6400-02', 'Sony A6400', 'Camera', 1, 1, NULL, NULL,
        DATETIME('now', '-7 days', 'localtime')),

       ('A6400-03', 'Sony A6400', 'Camera', 1, 0, '2',
        DATETIME('now', '-100 days', 'localtime'),
        DATETIME('now', '-100 days', 'localtime')),

       ('A6400-04', 'Sony A6400', 'Camera', 1, 0, 'invalid',
        DATETIME('now', '-350 days', 'localtime'),
        DATETIME('now', '-400 days')),

       ('Canon-01', 'Canon 860D', 'Camera', 1, 1, NULL, NULL,
        DATETIME('now', '-400 days', 'localtime')),

       ('Canon-02', 'Canon 860D', 'Camera', 1, 1, NULL, NULL,
        DATETIME('now', '-5 hours', 'localtime')),

       ('Canon-03', 'Canon 860D', 'Camera', 0, 0, '2',
        DATETIME('now', 'localtime'),
        DATETIME('now', '-2 days', 'localtime'));