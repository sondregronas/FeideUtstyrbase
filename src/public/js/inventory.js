let new_items = [];

// TODO: Massive refactor / cleanup would be nice - a lot of duplicate code and undocumented functions
// Overall it works-enough, but it's not very pretty

async function updateEditItemModal(name, description, category) {
  document.getElementById("edit_name").value = name;
  document.getElementById("edit_name_old").value = name;
  document.getElementById("edit_description").value = description;
  document.getElementById("edit_category").value = category;
}

function sanitizeItem(
  name_input,
  description_input,
  category_input,
  response_message_object
) {
  let name = name_input.value;
  let description = description_input.value;
  let category = category_input.value;

  response_message_object.innerHTML = "";
  response_message_object.classList.remove("success");
  response_message_object.classList.remove("error");

  if (!name || !description || !category) {
    response_message_object.classList.add("error");
    response_message_object.innerHTML = "Venligst fyll ut alle feltene";
    return false;
  }

  if (!checkSanitizedInput(name_input)) {
    response_message_object.classList.add("error");
    response_message_object.innerHTML = "Ugyldig navn";
    return false;
  }
  return true;
}

async function addItem() {
  let name = document.getElementById("name");
  let description = document.getElementById("description");
  let category = document.getElementById("category");

  let response_message = document.getElementById("response_message");

  if (!sanitizeItem(name, description, category, response_message)) return;

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
    addToTable(item);
    name.value = "";
    description.value = "";
    category.value = "";
  } else {
    response_message.classList.add("error");
    response_message.innerHTML = data.message;
  }
}

function deleteItem() {
  let name = document.getElementById("edit_name_old").value;
  // TODO: Send items to server
  if (confirm("Er du sikker på at du vil slette " + name + "?"))
    removeFromTable(name);
}

function saveChanges() {
  /**
   * @param {Object} old_item - The item before changes
   * @param {Object} new_item - The item after changes
   */
  let old_item_name = document.getElementById("edit_name_old").value;

  let name = document.getElementById("edit_name");
  let description = document.getElementById("edit_description");
  let category = document.getElementById("edit_category");

  let response_message = document.getElementById("edit_response_message");

  let new_item = {
    name: name.value,
    description: description.value,
    category: category.value,
    available: true,
  };

  if (!sanitizeItem(name, description, category, response_message)) return;

  // TODO: Send items to server

  removeFromTable(old_item_name);
  addToTable(new_item);
}

function removeFromTable(name) {
  let table = document.getElementById("inventory_table");
  for (let i = 0; i < table.rows.length; i++) {
    if (table.rows[i].cells[0].innerHTML.toLowerCase() === name.toLowerCase()) {
      table.deleteRow(i);
      break;
    }
  }
}

function addToTable(item) {
  let table = document.getElementById("inventory_table");
  let row = table.insertRow(-1);
  row.insertCell(0).innerHTML = item.name;
  row.insertCell(1).innerHTML = item.description;
  row.insertCell(2).innerHTML = item.category;
  row.insertCell(3).innerHTML = "Ny!";
}

function checkName(input, used_names) {
  used_names = used_names.concat(new_items.map((item) => item.name));
  if (!checkSanitizedInput(input)) {
    input.setAttribute("aria-invalid", "true");
    input.setAttribute("aria-describedby", "Invalid input");
    return;
  }
  if (used_names.includes(input.value)) {
    input.setAttribute("aria-invalid", "true");
    input.setAttribute("aria-describedby", "Name already in use");
  } else {
    input.setAttribute("aria-invalid", "false");
    input.removeAttribute("aria-describedby");
  }
}

function checkSanitizedInput(input, options = {}) {
  /**
   * @param {HTMLInputElement} input
   * @param {Object} options - Optional
   * @param {RegExp} options.expression - Optional, regex to test input against
   * @param {Boolean} options.only_invalid - Optional, only add aria-invalid if input is invalid, hides aria-invalid if input is valid
   * @returns {Boolean} - Returns true if input is valid, false if input is invalid
   */
  let regex = new RegExp(options.expression || /^[a-zA-Z0-9æøåÆØÅ# _-]+$/);
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

// TODO: Simplify this function
function sortTable(column) {
  let table,
    rows,
    switching,
    i,
    x,
    y,
    shouldSwitch,
    dir,
    switchcount = 0;
  table = document.getElementById("inventory_table");
  switching = true;
  dir = "asc";
  while (switching) {
    switching = false;
    rows = table.rows;
    for (i = 1; i < rows.length - 1; i++) {
      shouldSwitch = false;
      x = rows[i].getElementsByTagName("TD")[column];
      y = rows[i + 1].getElementsByTagName("TD")[column];
      if (dir == "asc") {
        if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
          shouldSwitch = true;
          break;
        }
      } else if (dir == "desc") {
        if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
          shouldSwitch = true;
          break;
        }
      }
    }
    if (shouldSwitch) {
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
      switchcount++;
    } else {
      if (switchcount == 0 && dir == "asc") {
        dir = "desc";
        switching = true;
      }
    }
  }
}

function searchTable(input) {
  /**
   * Search the inventory table for items, and hide items that don't match the search, searches column 0 and 2 (name and category)
   * @param {HTMLInputElement} input - The input element used to search the table
   * @returns {void} - Returns nothing, but hides items that don't match the search
   * @type {string}
   */
  let filter = input.value.toLowerCase();
  let table = document.getElementById("inventory_table");
  let tr = table.getElementsByTagName("tr");
  // Search both column 0 and 2 (name and category)
  for (let i = 0; i < tr.length; i++) {
    let td = tr[i].getElementsByTagName("td")[0];
    let td2 = tr[i].getElementsByTagName("td")[2];
    if (td || td2) {
      if (
        td.innerHTML.toLowerCase().indexOf(filter) > -1 ||
        td2.innerHTML.toLowerCase().indexOf(filter) > -1
      ) {
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";
      }
    }
  }
}
