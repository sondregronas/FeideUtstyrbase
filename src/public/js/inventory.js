let new_items = [];

let table_id = "inventory-table";

let edit_item_name = "edit-item-name";
let edit_item_name_old = "edit-item-name_old";
let edit_item_description = "edit-item-description";
let edit_item_category = "edit-item-category";
let edit_item_response_message = "edit-item-response-message";
let edit_item_default_response_message_text = document.getElementById(
  edit_item_response_message
).innerHTML;

let add_item_name = "add-item-name";
let add_item_description = "add-item-description";
let add_item_category = "add-item-category";
let add_item_response_message = "add-item-response-message";
let add_item_default_response_message_text = document.getElementById(
  add_item_response_message
).innerHTML;

// TODO: This is a bit messy, but it works
function updateEditItemModal(name, description, category) {
  /**
   * Updates the edit item modal with the item's data
   * @param name - The name of the item
   * @param description - The description of the item
   * @param category - The category of the item
   * @returns {void} - Updates the modal
   */
  let edit_name = document.getElementById(edit_item_name);
  edit_name.value = name;
  edit_name.removeAttribute("aria-invalid");
  edit_name.removeAttribute("aria-describedby");
  document.getElementById(edit_item_name_old).value = name;
  document.getElementById(edit_item_description).value = description;
  document.getElementById(edit_item_category).value = category;
  let response_message = document.getElementById(edit_item_response_message);
  response_message.innerHTML = edit_item_default_response_message_text;
  response_message.classList.remove("success");
  response_message.classList.remove("error");
}

// TODO: This is a bit messy, but it works
function resetAddItemModal() {
  /**
   * Resets the add item modal, removing all input and response messages
   * @returns {void} - Resets the modal
   */
  let add_name = document.getElementById(add_item_name);
  add_name.value = "";
  add_name.removeAttribute("aria-invalid");
  add_name.removeAttribute("aria-describedby");
  document.getElementById(add_item_description).value = "";
  document.getElementById(add_item_category).value = "";
  let response_message = document.getElementById(add_item_response_message);
  response_message.innerHTML = add_item_default_response_message_text;
  response_message.classList.remove("success");
  response_message.classList.remove("error");
}

function checkUniqueItemName(input, used_names) {
  /**
   * Checks if the input is a valid name, and that the name is not already in use.
   * @param {HTMLInputElement} input
   * @param {Array} used_names - Array of names that are already in use
   * @returns {Boolean} - Returns true if input is valid, false if input is invalid, and sets aria-invalid and aria-describedby attributes on input
   */
  used_names = used_names.concat(new_items.map((item) => item.name));

  // If the input is the same as the old name, it is valid
  if (input.value === document.getElementById(edit_item_name_old).value) {
    input.setAttribute("aria-invalid", "false");
    input.removeAttribute("aria-describedby");
    return true;
  }

  // Check if the input is valid using the _checkSanitizedInput function
  if (!_checkSanitizedInput(input)) {
    input.setAttribute("aria-invalid", "true");
    input.setAttribute("aria-describedby", "Invalid input");
    return;
  }

  // Check if the input is already in use
  if (used_names.includes(input.value)) {
    input.setAttribute("aria-invalid", "true");
    input.setAttribute("aria-describedby", "Name already in use");
  } else {
    input.setAttribute("aria-invalid", "false");
    input.removeAttribute("aria-describedby");
  }
}

function _verifyItemForm(
  name_input,
  description_input,
  category_input,
  response_message_object
) {
  /**
   * Verifies the input of the item form, and displays an error message if the input is invalid.
   * @param name_input - The name input element
   * @param description_input - The description input element
   * @param category_input - The category input element
   * @param response_message_object - The response message element
   * @returns {boolean} - Returns true if the input is valid, false if the input is invalid
   */
  let name = name_input.value;
  let description = description_input.value;
  let category = category_input.value;
  let old_name = document.getElementById(edit_item_name_old).value;

  response_message_object.innerHTML = "";
  response_message_object.classList.remove("success");
  response_message_object.classList.remove("error");

  if (!name || !description || !category) {
    response_message_object.classList.add("error");
    response_message_object.innerHTML = "Venligst fyll ut alle feltene";
    return;
  }

  let has_invalid_input = name_input.getAttribute("aria-invalid") === "true";
  let is_name_changed = name !== old_name;

  if (
    (has_invalid_input && is_name_changed) ||
    !_checkSanitizedInput(name_input)
  ) {
    response_message_object.classList.add("error");
    response_message_object.innerHTML =
      name_input.getAttribute("aria-describedby") || "Ugyldig navn";
    return;
  }

  return true;
}

function _checkSanitizedInput(input, options = {}) {
  /**
   * Checks if the input is valid, and sets aria-invalid and aria-describedby attributes on input
   * @param {HTMLInputElement} input
   * @param {Object} options - Optional
   * @param {RegExp} options.expression - Optional, regex to test input against
   * @param {Boolean} options.only_invalid - Optional, only add aria-invalid if input is invalid, hides aria-invalid if input is valid
   * @returns {Boolean} - Returns true if input is valid, false if input is invalid. Sets aria-invalid and aria-describedby attributes on input
   */
  let regex = new RegExp(options.expression || /^[a-zA-Z\dæøåÆØÅ# _-]+$/);
  let only_invalid = options.only_invalid || true;
  let valid = !!regex.test(input.value);

  if (valid && !only_invalid) {
    input.setAttribute("aria-invalid", "false");
    input.removeAttribute("aria-describedby");
  }
  if (!valid) {
    input.setAttribute("aria-invalid", "true");
    input.setAttribute("aria-describedby", "Invalid input");
  }
  if (only_invalid && (valid || !input.value)) {
    input.removeAttribute("aria-invalid");
    input.removeAttribute("aria-describedby");
  }
  return valid;
}

async function saveEditChanges(modalId) {
  /**
   * Saves changes to the currently edited item
   * @param {String} modalId - The id of the modal
   * @returns {Promise<boolean>} - Returns true if the changes were saved successfully, false if the changes were not saved
   */
  let name = document.getElementById(edit_item_name);
  let description = document.getElementById(edit_item_description);
  let category = document.getElementById(edit_item_category);
  let old_item_name = document.getElementById(edit_item_name_old).value;
  let response_message = document.getElementById(edit_item_response_message);

  let new_item = {
    name: name.value,
    description: description.value,
    category: category.value,
  };

  if (!_verifyItemForm(name, description, category, response_message)) return;

  _removeFromTable(old_item_name);
  _addToTable(new_item);
  await _updateItemInDB(old_item_name, new_item, response_message);
  // Reset the old name input
  document.getElementById(edit_item_name_old).value = "";
  closeModal(modalId);
}

async function deleteItemWithConfirm() {
  /**
   * Deletes an item from the database, with a confirmation dialog
   * @returns {boolean} - Returns true if the item is deleted, void if the item is not deleted
   */
  let old_name = document.getElementById(edit_item_name_old).value;
  let name = document.getElementById(edit_item_name).value;
  if (confirm(`Er du sikker på at du vil slette ${name}? Du kan ikke angre!`)) {
    await _removeItemFromDB(old_name);
    return true;
  }
}

async function _updateItemInDB(
  old_item_name,
  new_item,
  response_message = null
) {
  /**
   * Updates an item in the database
   * @param old_item_name - The old name of the item (used to find the item in the database)
   * @param new_item - The new item object
   * @param response_message - The response message element, to display a success or error message
   * @returns {Promise<void>} - Updates the item in the database, and displays a success or error message
   */
  let response = await fetch("/inventory/update", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ old_name: old_item_name, new_item: new_item }),
  });
  let data = await response.json();
  if (data.success && response_message) {
    response_message.classList.add("success");
    response_message.innerHTML = data.message;
  } else {
    response_message.classList.add("error");
    response_message.innerHTML = data.message;
  }
}

async function _removeItemFromDB(name) {
  /**
   * Removes an item from the database
   * @param name - The name of the item to remove
   * @returns {Promise<void>} - Removes the item from the database, and removes the item from the table if successful
   */
  let response = await fetch("/inventory/remove", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ name }),
  });
  let data = await response.json();
  if (data.success) {
    _removeFromTable(name);
  }
}

function _removeFromTable(name) {
  /**
   * Removes an item from the table, user should still refresh the page to see the changes
   * @param name - The name of the item to remove
   * @returns {void} - Removes the item from the table (NOTE: Does not remove the item from the database)
   * @type {HTMLElement}
   */
  let table = document.getElementById(table_id);
  for (let i = 0; i < table.rows.length; i++) {
    if (table.rows[i].cells[0].innerHTML.toLowerCase() === name.toLowerCase()) {
      table.deleteRow(i);
      break;
    }
  }
}

function _addToTable(item) {
  /**
   * Adds an item to the table, user should still refresh the page to see the changes
   * @param item - The item object
   * @returns {void} - Adds the item to the table (NOTE: Does not add the item to the database)
   */
  let table = document.getElementById(table_id);
  let row = table.insertRow(-1);
  row.insertCell(0).innerHTML = item.name;
  row.insertCell(1).innerHTML = item.description;
  row.insertCell(2).innerHTML = item.category;
  row.insertCell(3).innerHTML = "Ukjent";
  row.insertCell(4).innerHTML = "Nylig endret";
}

// TODO: This function does too much, split it up?
async function addItem() {
  let name = document.getElementById(add_item_name);
  let description = document.getElementById(add_item_description);
  let category = document.getElementById(add_item_category);

  let response_message = document.getElementById(add_item_response_message);

  if (!_verifyItemForm(name, description, category, response_message)) return;

  let item = {
    name: name.value,
    description: description.value,
    category: category.value,
    available: true,
  };

  let response = await fetch("/inventory/add", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(item),
  });
  let data = await response.json();
  if (data.success) {
    response_message.classList.add("success");
    response_message.innerHTML = data.message;
    new_items.push(item);
    _addToTable(item);
    name.value = "";
    description.value = "";
    category.value = "";
  } else {
    response_message.classList.add("error");
    response_message.innerHTML = data.message;
  }
}
