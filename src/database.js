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
    let stmt = db.prepare(`DELETE FROM ${dbutils.feide_table} WHERE sub = ?`);
    stmt.run(data.openid.sub);
  }

  let stmt = db.prepare(
    `INSERT INTO ${dbutils.feide_table} (sub, name, email, picture, affiliation, org) VALUES (?, ?, ?, ?, ?, ?)`
  );
  stmt.run(
    data.openid.sub,
    data.openid.name,
    data.openid.email,
    data.openid.picture || null,
    data.ext_info.eduPersonPrimaryAffiliation,
    data.groups[0].displayName
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

  let stmt = db.prepare(`SELECT * FROM ${dbutils.feide_table} WHERE sub = ?`);
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

  let stmt = db.prepare(`SELECT * FROM ${dbutils.feide_table} WHERE sub = ?`);
  let user = stmt.get(sub);

  db.close();

  return user !== undefined;
}

function getEmployeeFromName(name) {
  /**
   * Gets the teacher from the database
   * @param name - The teachers name
   * @returns {object} - The teacher object
   * @type {Database}
   */
  let db = new Sqlitedb(database, db_options);

  let stmt = db.prepare(
    `SELECT * FROM ${dbutils.feide_table} WHERE name = ? AND affiliation = 'employee'`
  );
  let teacher = stmt.get(name);

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
    `SELECT * FROM ${dbutils.feide_table} WHERE affiliation = 'employee'`
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
  //let teacher = getEmployeeFromName(user.classroom_teacher);
  //if (!teacher) throw new Error("Teacher not found in admins table");

  // If the user already exists, remove it first
  if (readRegisteredUser(sub)) {
    let stmt = db.prepare(
      `DELETE FROM ${dbutils.registered_users_table} WHERE sub = ?`
    );
    stmt.run(sub);
  }

  let updated_at = new Date();
  let expires_at = new Date(updated_at.getFullYear() + 1, 6, 1); // 1st of July next year

  let stmt = db.prepare(
    `INSERT INTO ${dbutils.registered_users_table} (name, classroom, classroom_teacher, school_email, personal_email, picture, updated_at, expires_at, sub) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`
  );
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
    `SELECT * FROM ${dbutils.registered_users_table} WHERE sub = ?`
  );
  let user = stmt.get(sub);

  db.close();

  return user;
}

function fetchRegisteredUsers(only_active = true) {
  /**
   * Gets all the users from the database
   * @returns {object} - The user object
   * @type {Database}
   */
  let db = new Sqlitedb(database, db_options);

  let stmt = db.prepare(
    `SELECT * FROM ${dbutils.registered_users_table} WHERE expires_at > ?`
  );

  let users = stmt.all(only_active ? new Date().getTime() : 0);

  db.close();

  // append fetchEmployees to list of users
  users = users.concat(fetchEmployees());

  return users;
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
      `INSERT INTO ${dbutils.inventory_table} (name, description, category, available, last_borrowed, last_checked) VALUES (?, ?, ?, ?, ?, ?)`
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

  db.close();
}

function getInventoryItems() {
  /**
   * Gets all the items from the inventory
   * @returns {object} - The item objects
   * @type {Database}
   */
  let db = new Sqlitedb(database, db_options);

  let stmt = db.prepare(`SELECT * FROM ${dbutils.inventory_table}`);
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
    `UPDATE ${dbutils.inventory_table} SET last_borrowed = ? WHERE name = ?`
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
    `UPDATE ${dbutils.inventory_table} SET name = ?, description = ?, category = ? WHERE name = ?`
  );
  stmt.run(
    new_item.name,
    new_item.description || null,
    new_item.category || null,
    old_name
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
    `DELETE FROM ${dbutils.inventory_table} WHERE name = ?`
  );
  stmt.run(name);

  db.close();
}

/*
  RENTED ITEMS
 */

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
}

module.exports = {
  initializeAll,
  addFeideUser,
  readFeideUser,
  addRegisteredUser,
  validateUser,
  readRegisteredUser,
  fetchRegisteredUsers,
  addInventoryItem,
  getInventoryItems,
  updateItemLastBorrowed,
  updateInventoryItemBasic,
  removeInventoryItem,
};
