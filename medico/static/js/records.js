// Get references to the input elements and the button
const nameInput = document.querySelector("name");
const rollNumberInput = document.querySelector("rollnumber");
const dateInput = document.getElementById("deadline");
const hostelInput = document.getElementById("hostel");
const addRecordButton = document.getElementById("add-task");

// Add class and text to the button
addRecordButton.innerHTML = "Add Record";
addRecordButton.classList.add("button");

const recordList = document.getElementById("task-list");

// Event listener for the "Add Record" button
addRecordButton.addEventListener("click", () => {
    const name = nameInput.value;
    const rollNumber = rollNumberInput.value;
    const date = dateInput.value;
    const hostel = hostelInput.value;

 // Function to add records
function addRecord() {
    // Get input values
    var name = document.getElementById("name").value;
    var rollNumber = document.getElementById("rollnumber").value;
    var date = document.getElementById("deadline").value;
    var hostel = document.getElementById("hostel").value;

    // Check if the inputs are empty or not selected
    if (name.trim() === "" || rollNumber.trim() === "" || date.trim() === "" || hostel === "----") {
        alert("Please fill in all fields.");
        return; // Don't add record if any field is empty or not selected
    }

    // Here you can proceed to add the record
    // For example, you might want to display or process the record
    console.log("Name:", name);
    console.log("Roll Number:", rollNumber);
    console.log("Date:", date);
    console.log("Hostel:", hostel);

    // You can add further logic to display or process the record here
}

// Event listener for the button
document.getElementById("add-task").addEventListener("click", addRecord);


    // Create a new record item
    const recordItem = document.createElement("div");
    recordItem.classList.add("record");
    recordItem.innerHTML = `
        <p>Name: ${name}</p>
        <p>Roll Number: ${rollNumber}</p>
        <p>Date: ${date}</p>
        <p>Hostel: ${hostel}</p>
        <button class="view">View</button>
    `;

    // Append the new record item to the record list
    recordList.appendChild(recordItem);

    // Clear the input fields
    nameInput.value = "";
    rollNumberInput.value = "";
    dateInput.value = "";
    hostelInput.value = "----";
});
