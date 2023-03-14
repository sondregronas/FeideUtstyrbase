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
  let selected_student_input = document.getElementById("selected_student");

  // Set the value of the hidden input
  let selected_user = document.getElementById("selected_user");
  selected_user.value = user_name;

  // Name to display on the button
  selected_student_input.innerHTML = `${user_name} (${affiliation})`;
  closeDropdown("user-select");
}

function lendGear() {
  let username = document.getElementById("selected_user");

  let start_date = document.getElementById("start_date");
  let end_date = document.getElementById("end_date");

  let gear = document.getElementById("gear");
  let comment = document.getElementById("comment");

  let data = {
    username: username.value,
    start_date: start_date.value,
    end_date: end_date.value,
    gear: gear.value,
    comment: comment.value,
  };

  console.log(data);

  // Clear fields
  username.value = "";
  start_date.value = "";
  end_date.value = "";
  gear.value = "";
  comment.value = "";
}
