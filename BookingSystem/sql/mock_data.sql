-- USERS
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

-- INVENTORY
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

-- REG OUT
INSERT INTO `audits` (`timestamp`, `event`, `message`)
VALUES (DATETIME('now', '-1 day', 'localtime'), 'REG_OUT',
        'Bee-Bot-02 ble registrert ut til Kari Elev (1C (Arne Underviser)) i 5 dager.'),
       (DATETIME('now', '-7 days', 'localtime'), 'REG_OUT',
        'Bee-Bot-03 ble registrert ut til Kari Elev (1C (Arne Underviser)) i 3 dager.'),
       (DATETIME('now', '-7 days', 'localtime'), 'REG_OUT',
        'A6400-03 ble registrert ut til Ekstra Langt Navn Som Er Ekstra Langt (1B (Jens Underviser)) i 4 dager.'),
       (DATETIME('now', '-350 days', 'localtime'), 'REG_OUT',
        'A6400-04 ble registrert ut til Per Elevnavn (3C (Siri Underviser)) i 6 dager.'),
       (DATETIME('now', '-400 days', 'localtime'), 'REG_OUT',
        'Canon-01 ble registrert ut til Per Elevnavn (3C (Siri Underviser)) i 2 dager.'),
       (DATETIME('now', '-5 hours', 'localtime'), 'REG_OUT',
        'Canon-02 ble registrert ut til Per Elevnavn (3C (Siri Underviser)) i 3 dager.');

-- REG IN
INSERT INTO `audits` (`timestamp`, `event`, `message`)
VALUES (DATETIME('now', '-55 days', 'localtime'), 'REG_IN', 'Bee-Bot-01 er nå tilgjengelig.'),
       (DATETIME('now', '-7 days', 'localtime'), 'REG_IN', 'Bee-Bot-03 er nå tilgjengelig.'),
       (DATETIME('now', '-400 days', 'localtime'), 'REG_IN', 'Canon-01 er nå tilgjengelig.'),
       (DATETIME('now', '-5 hours', 'localtime'), 'REG_IN', 'Canon-02 er nå tilgjengelig.');

-- POSTPONE
INSERT INTO `audits` (`timestamp`, `event`, `message`)
VALUES (DATETIME('now', '-1 day', 'localtime'), 'POSTPONE',
        'Bee-Bot-02 har fått utsatt frist til 01.01.2020 (Kari Elev (1C (Arne Underviser)))'),
       (DATETIME('now', '-7 days', 'localtime'), 'POSTPONE',
        'Bee-Bot-03 har fått utsatt frist til 01.01.2020 (Kari Elev (1C (Arne Underviser)))'),
       (DATETIME('now', '-7 days', 'localtime'), 'POSTPONE',
        'A6400-03 har fått utsatt frist til 01.01.2020 (Ekstra Langt Navn Som Er Ekstra Langt (1B (Jens Underviser)))'),
       (DATETIME('now', '-5 hours', 'localtime'), 'POSTPONE',
        'Canon-02 har fått utsatt frist til 01.01.2020 (Per Elevnavn (3C (Siri Underviser)))');

-- AVVIK (item specific)
INSERT INTO `audits` (`timestamp`, `event`, `message`)
VALUES (DATETIME('now', '-1 day', 'localtime'), 'AVVIK', 'Avvik på utstyr Bee-Bot-02: Mangler sd-kort'),
       (DATETIME('now', '-7 days', 'localtime'), 'AVVIK', 'Avvik på utstyr Bee-Bot-03: Mangler 2 batteri');

-- AVVIK (general)
INSERT INTO `audits` (`timestamp`, `event`, `message`)
VALUES (DATETIME('now', '-8 days', 'localtime'), 'AVVIK', 'Generelt avvik: Flere SD-kort mangler'),
       (DATETIME('now', '-5 days', 'localtime'), 'AVVIK', 'Generelt avvik: Defekt kameraplate');

-- ITEM_EDIT
INSERT INTO `audits` (`timestamp`, `event`, `message`)
VALUES (DATETIME('now', '-7 days', 'localtime'), 'ITEM_EDIT', 'Bee-Bot-03 ble endret. (name: be bot 03->Bee-Bot-03)'),
       (DATETIME('now', '-5 days', 'localtime'), 'ITEM_EDIT', 'A6400-01 ble endret. (category: Robot->Camera)');

-- ITEM_NEW (Add everything in the last 370 days)
INSERT INTO `audits` (`timestamp`, `event`, `message`)
VALUES (DATETIME('now', '-370 days', 'localtime'), 'ITEM_NEW',
        'Bee-Bot-01 ble lagt til. (Bee-Bot Den Nye Undervisningsrobotten - Robot)'),
       (DATETIME('now', '-370 days', 'localtime'), 'ITEM_NEW',
        'Bee-Bot-02 ble lagt til. (Bee-Bot Den Nye Undervisningsrobotten - Robot)'),
       (DATETIME('now', '-250 days', 'localtime'), 'ITEM_NEW',
        'Bee-Bot-03 ble lagt til. (Bee-Bot Den Nye Undervisningsrobotten - Robot)'),
       (DATETIME('now', '-250 days', 'localtime'), 'ITEM_NEW',
        'Bee-Bot-04 ble lagt til. (Bee-Bot Den Nye Undervisningsrobotten - Robot)'),
       (DATETIME('now', '-250 days', 'localtime'), 'ITEM_NEW',
        'Bee-Bot-05 ble lagt til. (Bee-Bot Den Nye Undervisningsrobotten - Robot)'),
       (DATETIME('now', '-18 days', 'localtime'), 'ITEM_NEW', 'A6300-01 ble lagt til. (Sony A6300 - Camera)'),
       (DATETIME('now', '-18 days', 'localtime'), 'ITEM_NEW', 'A6400-01 ble lagt til. (Sony A6400 - Camera)'),
       (DATETIME('now', '-17 days', 'localtime'), 'ITEM_NEW', 'A6400-02 ble lagt til. (Sony A6400 - Camera)'),
       (DATETIME('now', '-17 days', 'localtime'), 'ITEM_NEW', 'A6400-03 ble lagt til. (Sony A6400 - Camera)'),
       (DATETIME('now', '-17 days', 'localtime'), 'ITEM_NEW', 'A6400-04 ble lagt til. (Sony A6400 - Camera)'),
       (DATETIME('now', '-5 days', 'localtime'), 'ITEM_NEW', 'Canon-01 ble lagt til. (Canon 860D - Camera)'),
       (DATETIME('now', '-5 days', 'localtime'), 'ITEM_NEW', 'Canon-02 ble lagt til. (Canon 860D - Camera)'),
       (DATETIME('now', '-5 days', 'localtime'), 'ITEM_NEW', 'Canon-03 ble lagt til. (Canon 860D - Camera)');

-- ITEM_REM
INSERT INTO `audits` (`timestamp`, `event`, `message`)
VALUES (DATETIME('now', '-370 days', 'localtime'), 'ITEM_REM', 'Bee-Bot-05 ble slettet.'),
       (DATETIME('now', '-400 days', 'localtime'), 'ITEM_REM', 'A6300-01 ble slettet.');