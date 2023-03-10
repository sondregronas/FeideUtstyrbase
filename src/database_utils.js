let Sqlitedb = require("better-sqlite3")

const database = "database.sqlite";
const db_options = { verbose: console.log };

const feide_table = "feide_data";
const classrooms_table = "classrooms";
const registered_users_table = "registered_users";
const inventory_table = "inventory";
const rented_items_table = "rented_items";

const feideQuery = `CREATE TABLE IF NOT EXISTS ${feide_table} (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      hashed_identifier TEXT NOT NULL,
      name TEXT NOT NULL,
      email TEXT NOT NULL,
      picture TEXT,
      affiliation TEXT NOT NULL,
      org TEXT NOT NULL,
      UNIQUE(hashed_identifier)
    );`;

const classroomsQuery = `CREATE TABLE IF NOT EXISTS ${classrooms_table} (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      classroom_teacher TEXT,
      UNIQUE(name)
    );`;

const registeredUsersQuery = `CREATE TABLE IF NOT EXISTS ${registered_users_table} (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      classroom TEXT NOT NULL,
      classroom_teacher TEXT NOT NULL,
      school_email TEXT NOT NULL,
      personal_email TEXT,
      picture TEXT,
      updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
      expires_at DATETIME NOT NULL,
      banned BOOLEAN NOT NULL DEFAULT 0,
      banned_reason TEXT,
      last_banned_at DATETIME,
      hashed_identifier TEXT NOT NULL,
      UNIQUE(hashed_identifier)
    );`;

const inventoryQuery = `CREATE TABLE IF NOT EXISTS ${inventory_table} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        category TEXT,
        available BOOLEAN NOT NULL DEFAULT 1,
        UNIQUE(name)
    );`;

const rentedItemsQuery = `CREATE TABLE IF NOT EXISTS ${rented_items_table} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item TEXT NOT NULL,
        hashed_identifier TEXT NOT NULL,
        rented_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        due_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        checked_in_at DATETIME,
        UNIQUE(item, hashed_identifier)
    );`;

function _createTable(query) {
  /**
   * Creates a table, be careful with this function. It's not meant to be used outside this file
   * @type {Database}
   */
  let db = new Sqlitedb(database, db_options);
  db.exec(query);
  db.close();
}

module.exports = {
    // Constants
    database,
    db_options,
    // Tables
    feide_table,
    classrooms_table,
    registered_users_table,
    inventory_table,
    rented_items_table,
    // Queries
    feideQuery,
    classroomsQuery,
    registeredUsersQuery,
    inventoryQuery,
    rentedItemsQuery,

    // Functions
    _createTable
}