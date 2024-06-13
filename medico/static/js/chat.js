let audio1 = new Audio("https://s3-us-west-2.amazonaws.com/s.cdpn.io/242518/clickUp.mp3");

function chatOpen() {
    document.getElementById("chat-open").style.display = "none";
    document.getElementById("chat-close").style.display = "block";
    document.getElementById("chat-window1").style.display = "block";
    audio1.play();
}

function chatClose() {
    document.getElementById("chat-open").style.display = "block";
    document.getElementById("chat-close").style.display = "none";
    document.getElementById("chat-window1").style.display = "none";
    document.getElementById("chat-window2").style.display = "none";
    audio1.play();
}

function openConversation() {
    document.getElementById("chat-window2").style.display = "block";
    document.getElementById("chat-window1").style.display = "none";
    audio1.play();
}

function userResponse() {
    let userText = document.getElementById("textInput").value;
    if (userText === "") {
        alert("Please type something!");
    } else {
        appendMessage("user", userText);
        document.getElementById("textInput").value = "";
        sendMessageToBackend(userText);
    }
}

function appendMessage(sender, message) {
    let messageBox = document.getElementById("messageBox");
    let messageElement = document.createElement("div");
    messageElement.className = sender === "user" ? "first-chat" : "second-chat";
    messageElement.innerHTML = `<p>${message}</p><div class="arrow"></div>`;
    messageBox.appendChild(messageElement);
    messageBox.scrollTop = messageBox.scrollHeight;
    if (sender === "bot") {
        let audio = new Audio("https://downloadwap.com/content2/mp3-ringtones/tone/2020/alert/preview/56de9c2d5169679.mp3");
        audio.play();
    }
}

function sendMessageToBackend(message) {
    fetch("/chatbot", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => appendMessage("bot", data.response))
    .catch(error => console.error("Error:", error));
}

document.getElementById("textInput").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        userResponse();
    }
});
