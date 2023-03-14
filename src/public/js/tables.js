function toggleColumnVisibility(column, toggleBtn = null, tableID = null) {
  /**
   * Toggle the visibility of a column in the inventory table
   * @param {Number} column - The column to toggle, 0 = name, 1 = description, 2 = category, 3 = edit, 4 = delete
   * @param {HTMLButtonElement} toggleBtn - The button that toggles the visibility of the column
   * @returns {void} - Returns nothing, but toggles the visibility of the column
   */
  let table = document.getElementById(tableID);
  let rows = table.rows;
  for (let i = 0; i < rows.length; i++) {
    let row = rows[i];
    let cell = row.cells[column];
    if (cell.style.display === "none") {
      cell.style.display = "";
      if (toggleBtn) {
        toggleBtn.classList.remove("filter__btn--inactive");
      }
    } else {
      cell.style.display = "none";
      if (toggleBtn) {
        toggleBtn.classList.add("filter__btn--inactive");
      }
    }
  }
}

function sortTable(column, tableID = null) {
  /**
   * Sort a table by a column
   * @param {Number} column - The column to sort by, 0 = name, 1 = description, 2 = category, 3 = edit, 4 = delete
   * @param {String} tableID - The ID of the table to sort
   * @returns {void} - Returns nothing, but sorts the table visually
   */
  let table,
    rows,
    switching,
    i,
    x,
    y,
    shouldSwitch,
    dir,
    switchcount = 0;
  table = document.getElementById(tableID);
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

function searchTable(searchValue, tableID = null) {
  /**
   * Search the inventory table for items, and hide items that don't match the search, searches column 0, 1 and 2 (name, description and category)
   * @param {HTMLInputElement} searchValue - The input element to search for
   * @param {String} tableID - The ID of the table to search
   * @returns {void} - Returns nothing, but hides items that don't match the search
   * @type {string}
   */
  let filter = searchValue.toLowerCase();
  let table = document.getElementById(tableID);
  let tr = table.getElementsByTagName("tr");

  for (let i = 0; i < tr.length; i++) {
    let td = tr[i].getElementsByTagName("td")[0];
    let td1 = tr[i].getElementsByTagName("td")[1];
    let td2 = tr[i].getElementsByTagName("td")[2];
    if (td || td1 || td2) {
      if (
        td.innerHTML.toLowerCase().indexOf(filter) > -1 ||
        td1.innerHTML.toLowerCase().indexOf(filter) > -1 ||
        td2.innerHTML.toLowerCase().indexOf(filter) > -1
      ) {
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";
      }
    }
  }
  updateResultsCounter(`#${tableID} tr`);
}

function updateResultsCounter(
  query,
  counterText = "search_results_text",
  hasHeader = true
) {
  /**
   * Update the counter that shows how many items are shown in the inventory table
   * @param {String} query - The query to select the table rows
   * @param {String} counterText - The ID of the element to update (where the text is shown)
   * @param {Boolean} hasHeader - Whether or not the table has a header (as to not count the headers)
   * @type {HTMLElement}
   */
  let element = document.getElementById(counterText);
  let total = document.querySelectorAll(query);
  let shown = Array.from(total).filter((item) => item.offsetParent !== null);
  let totalCount = total.length - (hasHeader ? 1 : 0);
  let shownCount = shown.length - (hasHeader ? 1 : 0);
  element.innerHTML = `Viser ${shownCount} av ${totalCount} elementer`;
}
