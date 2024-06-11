let audio1 = new Audio(
    "https://s3-us-west-2.amazonaws.com/s.cdpn.io/242518/clickUp.mp3"
  );
  
  function chatOpen() {
    document.getElementById("chat-open").style.display = "none";
    document.getElementById("chat-close").style.display = "block";
    document.getElementById("chat-window1").style.display = "block";
  
    audio1.load();
    audio1.play();
  }
  
  function chatClose() {
    document.getElementById("chat-open").style.display = "block";
    document.getElementById("chat-close").style.display = "none";
    document.getElementById("chat-window1").style.display = "none";
    document.getElementById("chat-window2").style.display = "none";
  
    audio1.load();
    audio1.play();
  }
  
  function openConversation() {
    document.getElementById("chat-window2").style.display = "block";
    document.getElementById("chat-window1").style.display = "none";
  
    audio1.load();
    audio1.play();
  }
  
  // Gets the text from the input box (user)
  function userResponse() {
    let userText = document.getElementById("textInput").value;
  
    if (userText === "") {
      alert("Please type something!");
    } else {
      document.getElementById("messageBox").innerHTML += `<div class="first-chat">
        <p>${userText}</p>
        <div class="arrow"></div>
      </div>`;
  
      let audio3 = new Audio(
        "https://prodigits.co.uk/content/ringtones/tone/2020/alert/preview/4331e9c25345461.mp3"
      );
      audio3.load();
      audio3.play();
  
      document.getElementById("textInput").value = "";
      var objDiv = document.getElementById("messageBox");
      objDiv.scrollTop = objDiv.scrollHeight;
  
      sendMessageToBackend(userText);
    }
  }
  
  // Sends user message to the backend and handles the response
  function sendMessageToBackend(message) {
    fetch("/chatbot", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ message: message })
    })
      .then((response) => response.json())
      .then((data) => {
        adminResponse(data.response);
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }
  
  // Admin response to user's message
  function adminResponse(message) {
    document.getElementById("messageBox").innerHTML += `<div class="second-chat">
      <div class="circle" id="circle-mar"></div>
      <p>${message}</p>
      <div class="arrow"></div>
    </div>`;
  
    let audio3 = new Audio(
      "https://downloadwap.com/content2/mp3-ringtones/tone/2020/alert/preview/56de9c2d5169679.mp3"
    );
    audio3.load();
    audio3.play();
  
    var objDiv = document.getElementById("messageBox");
    objDiv.scrollTop = objDiv.scrollHeight;
  }
  
  // Press enter on keyboard and send message
  addEventListener("keypress", (e) => {
    if (e.keyCode === 13) {
      const e = document.getElementById("textInput");
      if (e === document.activeElement) {
        userResponse();
      }
    }
  });
  