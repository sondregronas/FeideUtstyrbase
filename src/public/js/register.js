document.getElementById("classroom").addEventListener("change", function () {
  let teacher = document.getElementById("classroom_teacher");
  let teacher_disabled = document.getElementById("classroom_teacher_disabled");

  let classroom_data = this.options[this.selectedIndex].getAttribute(
    "data-classroom_teacher"
  );

  teacher.value = classroom_data;
  teacher_disabled.value = classroom_data;
});
