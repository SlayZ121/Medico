const nameInput = document.getElementById("name");
const rollNumberInput = document.getElementById("rollNumber");
const dateInput = document.getElementById("deadline");
const hostelInput = document.getElementById("hostel");
const addTaskButton = document.getElementById("add-task");
const taskList = document.getElementById("task-list");
const modal = document.getElementById("task-modal");
const closeButton = document.querySelector(".close-button");
const modalDetails = document.getElementById("modal-details");

addTaskButton.addEventListener("click", () => {
    const name = nameInput.value;
    const rollNumber = rollNumberInput.value;
    const date = dateInput.value;
    const hostel = hostelInput.value;

    if (name.trim() === "" || rollNumber.trim() === "" || date.trim() === "" || hostel === "----") {
        alert("Please fill in all fields.");
        return; // Don't add task if any field is empty
    }

    // Create a new task item
    const taskItem = document.createElement("div");
    taskItem.classList.add("task");
    taskItem.innerHTML = `
        <p>Name: ${name}</p>
        <p>Roll Number: ${rollNumber}</p>
        <p>Date: ${date}</p>
        <p>Hostel: ${hostel}</p>
        <button class="view">View</button>
    `;

    taskList.appendChild(taskItem);

    // Clear the input fields
    nameInput.value = "";
    rollNumberInput.value = "";
    dateInput.value = "";
    hostelInput.value = "----";
});

// Event listener for the "View" button
taskList.addEventListener("click", (event) => {
    if (event.target.classList.contains("view")) {
        const taskItem = event.target.parentElement;
        modalDetails.innerHTML = taskItem.innerHTML; // Display the task details in the modal
        modal.style.display = "block"; // Show the modal
    }
});

closeButton.addEventListener("click", () => {
    modal.style.display = "none"; // Hide the modal when the close button is clicked
});

window.addEventListener("click", (event) => {
    if (event.target === modal) {
        modal.style.display = "none"; // Hide the modal when clicking outside of it
    }
});
