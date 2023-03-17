let used_names = [];

let table_id = "inventory-table";

let edit_item_modal_id = "edit_item";
let add_item_modal_id = "add_item";
let print_label_modal_id = "print_label";

let search_input_id = "search";

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
let add_item_label_variant = "add-item-label-variant";
let add_item_label_amount = "add-item-label-amount";
let add_item_default_response_message_text = document.getElementById(
  add_item_response_message
).innerHTML;

// TODO: This is a bit messy, but it works
function updateEditItemModal(item) {
  /**
   * Updates the edit item modal with the item's data
   * @param item - The item to update the modal with
   * @returns {void} - Updates the modal
   */
  let edit_name = document.getElementById(edit_item_name);

  let id = decodeURIComponent(item.name);
  let name = decodeURIComponent(item.description);
  let category = decodeURIComponent(item.category);

  edit_name.value = id;
  edit_name.removeAttribute("aria-invalid");
  edit_name.removeAttribute("aria-describedby");
  document.getElementById(edit_item_name_old).value = id;
  document.getElementById(edit_item_description).value = name;
  document.getElementById(edit_item_category).value = category;
  let response_message = document.getElementById(edit_item_response_message);
  response_message.innerHTML = edit_item_default_response_message_text;
  response_message.classList.remove("success");
  response_message.classList.remove("error");
}

function resetEditModal() {
  /**
   * Resets the edit item modal, removing all input and response messages
   */
  updateEditItemModal("", "", "");
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

function checkUniqueItemName(input) {
  /**
   * Checks if the input is a valid name, and that the name is not already in use.
   * @param {HTMLInputElement} input
   * @param {Array} used_names - Array of names that are already in use
   * @returns {Boolean} - Returns true if input is valid, false if input is invalid, and sets aria-invalid and aria-describedby attributes on input
   */
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

function closeEditModal(modalId, confirm = false) {
  /**
   * Closes the edit modal
   * @param {String} modalId - The id of the modal
   */
  resetEditModal();
  closeModal(modalId, confirm);
}

async function saveEditChanges() {
  /**
   * Saves changes to the currently edited item
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

  await _updateItemInDB(old_item_name, new_item, response_message);

  updateTable();
  response_message.classList.add("success");
  response_message.innerHTML = `Lagret endringer for '${new_item.name}'`;
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
    updateTable();
  }
}

function _addToTable(item) {
  /**
   * Adds an item to the table
   * @param item - The item to add to the table
   * @returns {HTMLTableRowElement} - Returns the row element that was added to the table
   */
  let table = document.getElementById(table_id);
  let tbody = table.getElementsByTagName("tbody")[0];
  let row = tbody.insertRow(-1);

  let last_borrowed = "Aldri";
  if (item.last_borrowed) {
    let date = new Date(item.last_borrowed.date).toLocaleDateString(locale, {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
    last_borrowed = `${item.last_borrowed.name} (${item.last_borrowed.classroom}) - ${date}`;
  }

  let parameters = JSON.stringify({
    name: encodeURIComponent(item.name),
    description: encodeURIComponent(item.description),
    category: encodeURIComponent(item.category),
  });
  parameters = parameters.replace(/"/g, "&quot;");

  // Edit button
  let options = `<a onclick="updateEditItemModal(${parameters}); openModal('${edit_item_modal_id}');">Rediger</a>`;
  // Print button
  options = `${options}&nbsp;|&nbsp<a onclick="updatePrintModal(${parameters}); openModal('${print_label_modal_id}');">Etikett</a>`;
  // Register as available button
  if (item.available) {
    options = `${options}&nbsp;|&nbsp<a href="#Not-Implemented"'>Lever</a>`;
  }

  row.insertCell(0).innerHTML = item.name;
  row.insertCell(1).innerHTML = item.description;
  row.insertCell(2).innerHTML = item.category;
  row.insertCell(3).innerHTML = last_borrowed;
  row.insertCell(4).innerHTML = options;
}

function updateTable() {
  /**
   * Updates the table with the items from the database, and updates the results counter
   * Call this function after adding, modifying or removing an item
   */
  fetch("/inventory/fetch")
    .then((response) => response.json())
    .then((data) => {
      let table = document.getElementById(table_id);
      let tbody = table.getElementsByTagName("tbody")[0];
      tbody.innerHTML = "";
      used_names = [];
      data.forEach((item) => {
        used_names.push(item.name);
        _addToTable(item);
      });
      updateResultsCounter(`#${table_id} tr`);
      searchTable(document.getElementById(search_input_id).value, table_id);
    });
}

// TODO: This function does too much, split it up?
async function addItem() {
  /**
   * Adds an item to the database, provided the form is valid, then updates the table
   * also prints a label for the item if the user specified an amount
   * @returns {Promise<void>} - Adds the item to the database, and updates the table
   */
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

  let result = await fetch("/inventory/add", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(item),
  });
  result.json().then(
    (data) => {
      response_message.classList.add("success");
      response_message.innerHTML = data.message;
      // Print label if amount is specified
      if (document.getElementById(add_item_label_amount).value) {
        response_message.innerHTML = `${response_message.innerHTML} - sender jobb til printer...`;
        printLabel(
          add_item_name,
          add_item_description,
          add_item_label_variant,
          add_item_label_amount
        );
      }
      // Clear form & update table
      name.value = "";
      description.value = "";
      category.value = "";
      updateTable();
    },
    (error) => {
      response_message.classList.add("error");
      response_message.innerHTML = data.message;
    }
  );
}
