let Sqlitedb = require("better-sqlite3");
let dbutils = require("./database_utils")

let database = dbutils.database
let db_options = dbutils.db_options

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
  if (readFeideUser(data.hashed_identifier)) {
    let stmt = db.prepare(
      `DELETE FROM ${dbutils.feide_table} WHERE hashed_identifier = ?`
    );
    stmt.run(data.hashed_identifier);
  }

  let stmt = db.prepare(
    `INSERT INTO ${dbutils.feide_table} (hashed_identifier, name, email, picture, affiliation, org) VALUES (?, ?, ?, ?, ?, ?)`
  );
  stmt.run(
    data.hashed_identifier,
    data.openid.name,
    data.openid.email,
    data.openid.picture || null,
    data.ext_info.eduPersonPrimaryAffiliation,
    data.groups[0].displayName
  );

  db.close();
}

function readFeideUser(hashed_identifier) {
  /**
   * Gets the user from the database
   * @param hashed_identifier - The users hashed token
   * @returns {object} - The user object
   * @type {Database}
   */
  let db = new Sqlitedb(database, db_options);

  let stmt = db.prepare(
    `SELECT * FROM ${dbutils.feide_table} WHERE hashed_identifier = ?`
  );
  let user = stmt.get(hashed_identifier);

  db.close();

  return user;
}

function validateUser(hashed_identifier) {
  /**
   * Checks if the user exists in the database
   * @param hashed_identifier - The users hashed token
   * @returns {boolean} - If the user exists
   * @type {Database}
   */
  let db = new Sqlitedb(database, db_options);

  let stmt = db.prepare(
    `SELECT * FROM ${dbutils.feide_table} WHERE hashed_identifier = ?`
  );
  let user = stmt.get(hashed_identifier);

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

function addRegisteredUser(
  hashed_identifier,
  classroom,
  classroom_teacher,
  personal_email
) {
  /**
   * Adds a user to the database
   * @param hashed_identifier - The users hashed_identifier (unique id)
   * @param classroom - The users classroom name
   * @param classroom_teacher - The users classroom teacher, must be a valid teacher
   * @param personal_email - The users personal email, optional
   * @returns {void}
   * @type {Database}
   */
  let db = new Sqlitedb(database, db_options);

  let feide_info = readFeideUser(hashed_identifier);
  if (!feide_info) throw new Error("User not found in feide table");

  // TEMPORARILY COMMENTED OUT
  //let teacher = getEmployeeFromName(user.classroom_teacher);
  //if (!teacher) throw new Error("Teacher not found in admins table");

  // If the user already exists, remove it first
  if (readRegisteredUser(hashed_identifier)) {
    let stmt = db.prepare(
      `DELETE FROM ${dbutils.registered_users_table} WHERE hashed_identifier = ?`
    );
    stmt.run(hashed_identifier);
  }

  let updated_at = new Date();
  let expires_at = new Date(updated_at.getFullYear() + 1, 6, 1); // 1st of July next year

  let stmt = db.prepare(
    `INSERT INTO ${dbutils.registered_users_table} (name, classroom, classroom_teacher, school_email, personal_email, picture, updated_at, expires_at, hashed_identifier) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`
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
    hashed_identifier
  );

  db.close();
}

function readRegisteredUser(hashed_identifier) {
  /**
   * Gets the user from the database
   * @param hashed_identifier - The users hashed_identifier (unique id)
   * @returns {object} - The user object
   * @type {Database}
   */
  let db = new Sqlitedb(database, db_options);

  let stmt = db.prepare(
    `SELECT * FROM ${dbutils.registered_users_table} WHERE hashed_identifier = ?`
  );
  let user = stmt.get(hashed_identifier);

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
   * @returns {boolean} - True if the item was added, false if it already exists
   * @type {Database}
   */
  let db = new Sqlitedb(database, db_options);

  try {
    let stmt = db.prepare(
      `INSERT INTO ${dbutils.inventory_table} (name, description, category, available) VALUES (?, ?, ?, ?)`
    );
    stmt.run(
      item.name,
      item.description || null,
      item.category || null,
      item.available || 1
    );
  } catch (e) {
    if (e.message.includes("UNIQUE constraint failed")) {
      console.log(`Item ${item.name} already exists`);
    } else {
      console.log(e.message);
    }
    db.close();
    return false;
  }

  db.close();
  return true;
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
  dbutils._createTable(dbutils.feideQuery)
  dbutils._createTable(dbutils.classroomsQuery)
  dbutils._createTable(dbutils.registeredUsersQuery)
  dbutils._createTable(dbutils.inventoryQuery)
  dbutils._createTable(dbutils.rentedItemsQuery)
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
};
