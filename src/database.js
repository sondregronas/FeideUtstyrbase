let Sqlitedb = require("better-sqlite3");
let dbutils = require("./database_utils");

let database = dbutils.database;
let db_options = dbutils.db_options;

/*
  FEIDE
 */

function addFeideUser(data) {
  /**
   * Adds a user to the database
   * @param data - The data from the feide api (clientInfo)
   * @returns {void}
   * @type {Database}
   */
  let db = new Sqlitedb(database, db_options);

  // If the user already exists, remove it first
  if (readFeideUser(data.openid.sub)) {
    let stmt = db.prepare(`DELETE
                           FROM ${dbutils.feide_table}
                           WHERE sub = ?`);
    stmt.run(data.openid.sub);
  }

  let stmt = db.prepare(
    `INSERT INTO ${dbutils.feide_table} (sub, name, email, picture, affiliation, org)
     VALUES (?, ?, ?, ?, ?, ?)`
  );
  stmt.run(
    data.openid.sub,
    data.openid.name,
    data.openid.email,
    data.openid.picture || null,
    data.ext_info.eduPersonPrimaryAffiliation,
    data.groups[0].displayName
  );

  addAudit(
    `Added user ${data.openid.name} (${data.openid.sub}) to the database`
  );

  db.close();
}

function readFeideUser(sub) {
  /**
   * Gets the user from the database
   * @param sub - The users hashed token
   * @returns {object} - The user object
   * @type {Database}
   */
  let db = new Sqlitedb(database, db_options);

  let stmt = db.prepare(`SELECT *
                         FROM ${dbutils.feide_table}
                         WHERE sub = ?`);
  let user = stmt.get(sub);

  db.close();

  return user;
}

function validateUser(sub) {
  /**
   * Checks if the user exists in the database
   * @param sub - The users hashed token
   * @returns {boolean} - If the user exists
   * @type {Database}
   */
  let db = new Sqlitedb(database, db_options);

  let stmt = db.prepare(`SELECT *
                         FROM ${dbutils.feide_table}
                         WHERE sub = ?`);
  let user = stmt.get(sub);

  db.close();

  return user !== undefined;
}

function getEmployeeFromSub(sub) {
  /**
   * Gets the teacher from the database
   * @param name - The teachers name
   * @returns {object} - The teacher object
   * @type {Database}
   */
  let db = new Sqlitedb(database, db_options);

  let stmt = db.prepare(
    `SELECT *
     FROM ${dbutils.feide_table}
     WHERE sub = ?
       AND affiliation = 'employee'`
  );
  let teacher = stmt.get(sub);

  db.close();

  return teacher;
}

function fetchEmployees() {
  /**
   * Gets all the teachers from the database
   * @returns {object} - The teacher objects
   * @type {Database}
   */
  let db = new Sqlitedb(database, db_options);

  let stmt = db.prepare(
    `SELECT *
     FROM ${dbutils.feide_table}
     WHERE affiliation = 'employee'`
  );
  let teachers = stmt.all();

  db.close();

  return teachers;
}

/*
  CLASSROOMS
 */

/*
  REGISTERED USERS
 */

function addRegisteredUser(sub, classroom, classroom_teacher, personal_email) {
  /**
   * Adds a user to the database
   * @param sub - The users sub (unique id)
   * @param classroom - The users classroom name
   * @param classroom_teacher - The users classroom teacher, must be a valid teacher
   * @param personal_email - The users personal email, optional
   * @returns {void}
   * @type {Database}
   */
  let db = new Sqlitedb(database, db_options);

  let feide_info = readFeideUser(sub);
  if (!feide_info) throw new Error("User not found in feide table");

  // TEMPORARILY COMMENTED OUT
  //let teacher = getEmployeeFromSub(sub);
  //if (!teacher) throw new Error("Teacher not found in admins table");

  let stmt = db.prepare(
    `INSERT INTO ${dbutils.registered_users_table} (name, classroom, classroom_teacher, school_email, personal_email,
                                                    picture, updated_at, expires_at, sub)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`
  );

  // If the user already exists, update it instead
  if (readRegisteredUser(sub)) {
    stmt = db.prepare(
      `UPDATE ${dbutils.registered_users_table}
       SET name              = ?,
           classroom         = ?,
           classroom_teacher = ?,
           school_email      = ?,
           personal_email    = ?,
           picture           = ?,
           updated_at        = ?,
           expires_at        = ?
       WHERE sub = ?`
    );
  }

  let updated_at = new Date();
  let expires_at = new Date(updated_at.getFullYear() + 1, 6, 1); // 1st of July next year

  stmt.run(
    feide_info.name,
    classroom,
    classroom_teacher,
    feide_info.email,
    personal_email || null,
    feide_info.picture || null,
    updated_at.toISOString(),
    expires_at.toISOString(),
    sub
  );

  addAudit(`Added user ${feide_info.name} to the database`);

  db.close();
}

function readRegisteredUser(sub) {
  /**
   * Gets the user from the database
   * @param sub - The users sub (unique id)
   * @returns {object} - The user object
   * @type {Database}
   */
  let db = new Sqlitedb(database, db_options);

  let stmt = db.prepare(
    `SELECT *
     FROM ${dbutils.registered_users_table}
     WHERE sub = ?`
  );
  let user = stmt.get(sub);

  db.close();

  return user;
}

function readAllActiveUsers(only_active = true) {
  /**
   * Gets all the users from the database
   * @returns {object} - The user object
   * @type {Database}
   */
  let db = new Sqlitedb(database, db_options);

  let stmt = db.prepare(
    `SELECT *
     FROM ${dbutils.registered_users_table}
     WHERE expires_at > ?`
  );

  let users = stmt.all(only_active ? new Date().getTime() : 0);

  db.close();

  // append fetchEmployees to list of users
  users = users.concat(fetchEmployees());

  return users;
}

function updateUser(userdata) {
  /**
   * Updates a user in the database
   * @param userdata - The user object
   * @returns {void}
   * @type {Database}
   */
  let db = new Sqlitedb(database, db_options);

  let old_user = readRegisteredUser(userdata.sub);

  let stmt = db.prepare(
    `UPDATE ${dbutils.registered_users_table}
     SET name              = ?,
         classroom         = ?,
         classroom_teacher = ?,
         personal_email    = ?,
         banned            = ?,
         banned_reason     = ?,
         updated_at        = ?
     WHERE sub = ?`
  );

  let updated_at = new Date();

  stmt.run(
    userdata.name,
    userdata.classroom,
    userdata.classroom_teacher,
    userdata.personal_email || null,
    userdata.banned ? 1 : 0,
    userdata.banned_reason || null,
    updated_at.getTime(),
    userdata.sub
  );

  let new_user = readRegisteredUser(userdata.sub);

  let audit_message = `Updated user ${userdata.name}. Diff: `;
  for (let key in old_user) {
    if (key === "updated_at") continue;
    if (old_user[key] !== new_user[key]) {
      audit_message += `${key}: ${old_user[key]} -> ${new_user[key]}, `;
    }
  }
  addAudit(audit_message);

  db.close();
}

function deactivateUser(sub) {
  /**
   * Deactivates a user
   * @param sub - The users sub (unique id)
   * @returns {void}
   * @type {Database}
   */
  let db = new Sqlitedb(database, db_options);

  let stmt = db.prepare(
    `UPDATE ${dbutils.registered_users_table}
     SET expires_at = ?
     WHERE sub = ?`
  );

  stmt.run(0, sub);

  let userinfo = readRegisteredUser(sub);

  addAudit({
    action: `Deactivated user ${userinfo.name} (${userinfo.sub})`,
  });

  db.close();
}

/*
  INVENTORY
 */

function addInventoryItem(item) {
  /**
   * Adds an item to the inventory
   * @param item - The item object
   * @returns {void}
   * @type {Database}
   */
  let db = new Sqlitedb(database, db_options);

  try {
    let stmt = db.prepare(
      `INSERT INTO ${dbutils.inventory_table} (name, description, category, available, last_borrowed, last_checked)
       VALUES (?, ?, ?, ?, ?, ?)`
    );
    stmt.run(
      item.name,
      item.description || null,
      item.category || null,
      1,
      JSON.stringify(item.last_borrowed) || null,
      item.last_checked || new Date().getTime()
    );
  } catch (e) {
    db.close();
    if (e.message.includes("UNIQUE constraint failed")) {
      throw `Item ${item.name} already exists`;
    }
    throw e.message;
  }

  addAudit(
    `Added item ${item.name} to inventory (category: ${item.category}), description: ${item.description}`
  );

  db.close();
}

function getInventoryItems() {
  /**
   * Gets all the items from the inventory
   * @returns {object} - The item objects
   * @type {Database}
   */
  let db = new Sqlitedb(database, db_options);

  let stmt = db.prepare(`SELECT *
                         FROM ${dbutils.inventory_table}
                         ORDER BY LOWER(name)`);

  let items = stmt.all();

  items.forEach((item) => {
    if (item.last_borrowed) item.last_borrowed = JSON.parse(item.last_borrowed);
  });

  db.close();

  return items;
}

function updateItemLastBorrowed(name, last_borrowed) {
  /**
   * Updates the last borrowed date of an item
   * @param name - The name of the item
   * @param last_borrowed - The last borrowed date
   * @returns {void}
   * @type {Database}
   */
  let db = new Sqlitedb(database, db_options);

  let stmt = db.prepare(
    `UPDATE ${dbutils.inventory_table}
     SET last_borrowed = ?
     WHERE name = ?`
  );
  stmt.run(JSON.stringify(last_borrowed), name);

  db.close();
}

function updateInventoryItemBasic(old_name, new_item) {
  /**
   * Updates an item in the inventory
   * @param old_name - The old name of the item
   * @param new_item - The new item object
   * @returns {void}
   * @type {Database}
   */
  let db = new Sqlitedb(database, db_options);

  let stmt = db.prepare(
    `UPDATE ${dbutils.inventory_table}
     SET name        = ?,
         description = ?,
         category    = ?
     WHERE name = ?`
  );
  stmt.run(
    new_item.name,
    new_item.description || null,
    new_item.category || null,
    old_name
  );

  addAudit(
    `Updated item ${new_item.name} in inventory. (Category: ${new_item.category}, Description: ${new_item.description})`
  );

  db.close();
}

function removeInventoryItem(name) {
  /**
   * Deletes an item from the inventory
   * @param name - The name of the item
   * @returns {void}
   * @type {Database}
   */
  let db = new Sqlitedb(database, db_options);

  let stmt = db.prepare(
    `DELETE
     FROM ${dbutils.inventory_table}
     WHERE name = ?`
  );
  stmt.run(name);

  addAudit(`Removed item ${name} from inventory`);

  db.close();
}

/*
  RENTED ITEMS
 */

/*
  AUDIT LOG
 */

function addAudit(action) {
  /**
   * Adds an action to the audit log
   * @param action - The action object
   * @returns {void}
   * @type {Database}
   */
  let db = new Sqlitedb(database, db_options);

  let stmt = db.prepare(
    `INSERT INTO ${dbutils.audit_log_table} (event, timestamp)
     VALUES (?, ?)`
  );

  stmt.run(action, new Date().getTime());

  db.close();
}

function readAudits(count, offset = 0) {
  /**
   * Reads the audit log
   * @param count - The number of audits to read
   * @returns {object} - The audit objects
   * @type {Database}
   */
  let db = new Sqlitedb(database, db_options);

  let stmt = db.prepare(
    `SELECT *
     FROM ${dbutils.audit_log_table}
     ORDER BY timestamp DESC
     LIMIT ? OFFSET ?`
  );

  let audits = stmt.all(count, offset);

  db.close();

  return audits;
}

function addLend(data) {
  /**
   * Adds a lend to the database
   * @param data - The lend data
   * @returns {void}
   * @type {Database}
   */
  let db = new Sqlitedb(database, db_options);

  let stmt = db.prepare(
    `INSERT INTO ${dbutils.rented_items_table} (item, sub, due_at)
     VALUES (?, ?, ?)`
  );

  let stmt_inventory = db.prepare(
    `UPDATE ${dbutils.inventory_table}
     SET available     = 0,
         last_borrowed = ?,
         last_checked  = ?
     WHERE name = ?`
  );

  let user_info = readRegisteredUser(data.sub) || getEmployeeFromSub(data.sub);
  let due_at = new Date().getTime() + data.days * 24 * 60 * 60 * 1000;

  //for item in data.gear
  for (let item of data.gear) {
    stmt.run(item, data.sub, due_at);
    stmt_inventory.run(
      JSON.stringify({
        name: user_info.name,
        date: new Date().getTime(),
        due_date: due_at,
        classroom: user_info.classroom || "Ansatt",
      }),
      new Date().getTime(),
      item
    );
  }

  addAudit(
    `Lent ${data.gear.join(", ")} to ${user_info.name} (${
      user_info.classroom || "Ansatt"
    }) for ${data.days} days`
  );

  db.close();
}

/*
  Initialize / Exports
 */

function initializeAll() {
  /**
   * Initializes all the databases, should be called on startup
   * @returns {void}
   */
  dbutils._createTable(dbutils.feideQuery);
  dbutils._createTable(dbutils.classroomsQuery);
  dbutils._createTable(dbutils.registeredUsersQuery);
  dbutils._createTable(dbutils.inventoryQuery);
  dbutils._createTable(dbutils.rentedItemsQuery);
  dbutils._createTable(dbutils.auditLogQuery);
}

module.exports = {
  initializeAll,
  addFeideUser,
  readFeideUser,
  addRegisteredUser,
  validateUser,
  readRegisteredUser,
  readAllActiveUsers,
  updateUser,
  deactivateUser,
  addInventoryItem,
  getInventoryItems,
  updateItemLastBorrowed,
  updateInventoryItemBasic,
  removeInventoryItem,
  addAudit,
  readAudits,
  addLend,
};
