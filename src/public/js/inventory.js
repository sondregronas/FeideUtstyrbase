async function addItem() {
  let name = document.getElementById("name");
  let description = document.getElementById("description");
  let category = document.getElementById("category");

  let response_message = document.getElementById("response_message");
  response_message.innerHTML = "";
  response_message.classList.remove("success");
  response_message.classList.remove("error");

  if (!name.value || !description.value || !category.value) {
    response_message.classList.add("error");
    response_message.innerHTML = "Venligst fyll ut alle feltene";
    return;
  }

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
  } else {
    response_message.classList.add("error");
    response_message.innerHTML = data.message;
    return;
  }

  name.value = "";
  description.value = "";
  category.value = "";
}

function checkName(input, used_names) {
  if (used_names.includes(input.value)) {
    input.setAttribute("aria-invalid", "true");
    input.setAttribute("aria-describedby", "Name already in use");
  } else {
    input.setAttribute("aria-invalid", "false");
    input.removeAttribute("aria-describedby");
  }
}

function regexCheck(input, regex) {
  if (!input.value.match(regex)) {
    input.value = input.value.slice(0, -1);
  }
}
