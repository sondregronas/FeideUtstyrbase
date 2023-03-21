function _addToTable(user) {
  /**
   * Adds an user to the table
   * @param user - The item to add to the table
   * @returns {HTMLTableRowElement} - Returns the row element that was added to the table
   */
  let table = document.getElementById('users-table');
  let tbody = table.getElementsByTagName("tbody")[0];
  let row = tbody.insertRow(-1);

  let is_banned = user.banned;
  let status = 'Aktiv';
  let kommentar = '';
  if (is_banned) {
    status = `Bannlyst siden ${new Date(user.last_banned_at).toLocaleDateString()}`;
    kommentar = user.banned_reason;
  }

  let parameters = JSON.stringify({
    name: encodeURIComponent(user.name),
    classroom: encodeURIComponent(user.classroom),
    classroom_teacher: encodeURIComponent(user.classroom_teacher),
    personal_email: encodeURIComponent(user.personal_email),
    banned: encodeURIComponent(user.banned),
    banned_reason: encodeURIComponent(user.banned_reason),
    sub: encodeURIComponent(user.sub)
  });
  parameters = parameters.replace(/"/g, "&quot;");

  let classroom = 'Ansatt';
  let options = 'Kan ikke redigere ansatte'
  if (user.classroom_teacher) {
    classroom = `${user.classroom} (${user.classroom_teacher})`;
    options = `<a onclick="updateEditUserModal(${parameters}); openModal('edit-user-modal');">Rediger</a>`;
  }

  row.insertCell(0).innerHTML = user.name;
  row.insertCell(1).innerHTML = classroom;
  row.insertCell(2).innerHTML = status || 'Ukjent';
  row.insertCell(3).innerHTML = kommentar || '';
  row.insertCell(4).innerHTML = options;

  if (user.banned) {
    row.cells[0].classList.add('banned');
    row.cells[1].classList.add('banned');
    row.cells[2].classList.add('banned');
    row.cells[3].classList.add('banned');
  }
}

function updateTable() {
  /**
   * Updates the table with the items from the database, and updates the results counter
   * Call this function after adding, modifying or removing an item
   */
  fetch("/users/fetch")
    .then((response) => response.json())
    .then((data) => {
      let table = document.getElementById('users-table');
      let tbody = table.getElementsByTagName("tbody")[0];
      tbody.innerHTML = "";
      data.forEach((user) => {
        _addToTable(user);
      });
      updateResultsCounter(`#users-table tr`);
      searchTable(document.getElementById('search-users').value, 'users-table');
    });
}

function updateEditUserModal(user) {
  /**
   * Updates the modal that is used to edit an item
   * @param {Object} user - The user to edit
   */
  document.getElementById('edit-user-name').value = decodeURIComponent(user.name);
  document.getElementById('edit-user-classroom').value = decodeURIComponent(user.classroom);
  document.getElementById('edit-user-personal-email').value = decodeURIComponent(user.personal_email) === 'null' ? '' : decodeURIComponent(user.personal_email)
  document.getElementById('classroom_teacher_disabled').value = decodeURIComponent(user.classroom_teacher);
  document.getElementById('classroom_teacher').value = decodeURIComponent(user.classroom_teacher);
  document.getElementById('edit-user-banned').checked = decodeURIComponent(user.banned) === "1";
  document.getElementById('edit-user-banned-reason').value = decodeURIComponent(user.banned_reason);
  document.getElementById('edit-user-sub').value = decodeURIComponent(user.sub);
}

function closeEditModal() {
  /**
   * Closes the edit modal
   */
  document.getElementById('edit-user-name').value = '';
  document.getElementById('edit-user-classroom').value = '';
  document.getElementById('edit-user-personal-email').value = '';
  document.getElementById('classroom_teacher_disabled').value = '';
  document.getElementById('classroom_teacher').value = '';
  document.getElementById('edit-user-banned').checked = false;
  document.getElementById('edit-user-banned-reason').value = '';
  document.getElementById('edit-user-sub').value = '';
  closeModal('edit-user-modal');
}

function deactivateUserWithConfirm() {
  /**
   * Deletes the item with a confirmation prompt
   */
  let name = document.getElementById('edit-user-name').value;
  let sub = document.getElementById('edit-user-sub').value;
  if (confirm(`Er du sikker på at du vil gjøre ${name} inaktiv?`)) {
    deactivateUser(sub);
    closeEditModal();
  }
}

function deactivateUser(sub) {
  /**
   * Deletes the item with the given sub
   * @param sub - The sub of the item to delete
   */
  fetch(`/users/deactivate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      sub: encodeURIComponent(sub)
    })
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        updateTable();
      } else {
        alert('Noe gikk galt, prøv igjen senere');
      }
    });
}

async function saveEditChanges() {
  /**
   * Saves the changes made to the item
   */
  let name = document.getElementById('edit-user-name').value;
  let classroom = document.getElementById('edit-user-classroom').value;
  let classroom_teacher = document.getElementById('classroom_teacher').value;
  let personal_email = document.getElementById('edit-user-personal-email').value;
  let banned = document.getElementById('edit-user-banned').checked;
  let banned_reason = document.getElementById('edit-user-banned-reason').value;
  let sub = document.getElementById('edit-user-sub').value;

  let parameters = {
    "name": name,
    "classroom": classroom,
    "classroom_teacher": classroom_teacher,
    "personal_email": personal_email,
    "banned": banned,
    "banned_reason": banned_reason,
    "sub": sub
  };

  let result = await fetch(`/users/update`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(parameters)
  });
  result.json().then((data) => {
    if (data.success) {
      updateTable();
      closeEditModal('edit-user-modal');
    } else {
      alert('Noe gikk galt, prøv igjen senere');
    }
  });
}