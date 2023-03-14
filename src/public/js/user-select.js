function filterStudents(search_value) {
  let userlist = document.getElementById("user-list");
  let users = userlist.getElementsByTagName("li");
  for (let i = 0; i < users.length; i++) {
    let user = users[i];
    let name = user.innerHTML;
    if (name.toLowerCase().includes(search_value.toLowerCase())) {
      user.classList.remove("hidden");
    } else {
      user.classList.add("hidden");
    }
  }
}

function selectStudent(user_name, affiliation) {
  let selected_student_input = document.getElementById("selected_user--btn");

  // Set the value of the hidden input
  let selected_user = document.getElementById("selected_user");
  selected_user.value = user_name;

  // Name to display on the button
  selected_student_input.innerHTML = `${user_name} (${affiliation})`;
  closeModal("user-select");
}

function sortUserList() {
  let userlist = document.getElementById("user-list");
  let users = userlist.getElementsByTagName("li");
  let user_array = [];
  for (let i = 0; i < users.length; i++) {
    user_array.push(users[i]);
  }
  user_array.sort((a, b) => {
    if (a.innerText < b.innerText) {
      return -1;
    } else if (a.innerText > b.innerText) {
      return 1;
    } else {
      return 0;
    }
  });
  for (let i = 0; i < user_array.length; i++) {
    userlist.appendChild(user_array[i]);
  }
}

window.onload = function () {
  sortUserList();
};
