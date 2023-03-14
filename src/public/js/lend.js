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
