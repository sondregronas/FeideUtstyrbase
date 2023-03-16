const printserver = "http://localhost:5000";

function updatePrintModal(item_id, item_name, category = null) {
  /**
   * Updates the print modal with the item id and name
   * @param item_id - The id of the item
   * @param item_name - The name of the item
   * @param category - The category of the item (unused)
   * @returns {void} - but should update the print modal values
   */
  let print_id = document.getElementById("print-label-item-id");
  let print_name = document.getElementById("print-label-item-name");
  let print_amount = document.getElementById("print-label-amount");

  print_id.value = item_id;
  print_name.value = item_name;
  print_amount.value = 1;

  updateLabelPreview();
}

function updateLabelPreview() {
  /**
   * Updates the label preview
   * @returns {void} - but should update the label preview image
   */
  let item_id = document.getElementById("print-label-item-id").value;
  let item_name = document.getElementById("print-label-item-name").value;
  let variant = document.getElementById("print-label-variant").value;

  let preview_endpoint = `${printserver}/preview?id=${item_id}&name=${item_name}&variant=${variant}`;
  let print_preview = document.getElementById("label-preview");

  fetch(preview_endpoint)
    .then((r) => r.blob())
    .then((blob) => {
      print_preview.src = URL.createObjectURL(blob);
    });
}

function printLabel(
  input_id,
  input_name,
  input_variant = undefined,
  input_amount = undefined
) {
  /**
   * Sends a print job to the printer, if the input is valid
   * @returns {void} - but should physically print a label
   */
  let item_id = document.getElementById(input_id).value;
  let item_name = document.getElementById(input_name).value;
  let variant = document.getElementById(input_variant).value || "default";
  let amount = document.getElementById(input_amount).value || 1;

  if (!item_id || !item_name || amount < 1) {
    console.log("Invalid print job");
    return;
  }

  let print_endpoint = `${printserver}/print`;

  fetch(print_endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      id: item_id,
      name: item_name,
      variant: variant,
      count: amount,
    }),
  }).then((r) => {
    if (r.status === 200) {
      console.log("Print job successfully sent to printer");
    } else {
      console.log("Label printing failed");
    }
  });
}

function enforceMinMax(element, min, max) {
  /**
   * Enforces a minimum and maximum value for an input element
   * @param element - The input element
   * @param min - The minimum value
   * @param max - The maximum value
   * @returns {void} - Sets the value of the input element to the min or max if it is out of bounds
   */
  if (element.value < min) {
    element.value = min;
  } else if (element.value > max) {
    element.value = max;
  }
}
