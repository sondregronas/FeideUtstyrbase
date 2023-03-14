function openModal(id) {
  /**
   * Opens a modal
   * @param id - The id of the modal to open
   * @type {HTMLElement}
   */
  let modal = document.getElementById(id);
  modal.classList.add("modal-open");
}

function closeModal(id, confirm_close = false, callback = null) {
  /**
   * Closes a modal
   * @param id - The id of the modal to close
   * @type {HTMLElement}
   */
  let modal = document.getElementById(id);

  if (confirm_close) {
    if (!confirm("Er du sikker på at du vil lukke vinduet?")) {
      return;
    }
  }

  modal.classList.remove("modal-open");

  if (callback) {
    callback();
  }
}

function openDropdown(id) {
  /**
   * Opens a dropdown
   * @param id - The id of the dropdown to open
   * @type {HTMLElement}
   */
  let dropdown = document.getElementById(id);
  dropdown.classList.add("dropdown-open");
}

function closeDropdown(id) {
  /**
   * Closes a dropdown
   * @param id - The id of the dropdown to close
   * @type {HTMLElement}
   */
  let dropdown = document.getElementById(id);
  dropdown.classList.remove("dropdown-open");
}

function toggleDropdown(id) {
  /**
   * Toggles a dropdown
   * @param id - The id of the dropdown to toggle
   * @type {HTMLElement}
   */
  let dropdown = document.getElementById(id);
  dropdown.classList.toggle("dropdown-open");
}
