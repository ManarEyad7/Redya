const chatInput = document.getElementById("chat-input"); 
const sendButton = document.querySelector("#send-btn");
const chatContainer = document.querySelector(".chat-container"); 
const themeButton = document.querySelector("#theme-btn");
const deleteButton = document.querySelector("#delete-btn");

let userText = null;
const API_KEY = "PASTE-YOUR-API-KEY-HERE"; // Paste your API key here

const loadDataFromLocalstorage = () => {
    // Remove chats from local storage at page load
    localStorage.removeItem("all-chats"); // This will clear chats on page reload

    const themeColor = localStorage.getItem("themeColor");

    document.body.classList.toggle("light-mode", themeColor === "light_mode");
    themeButton.innerText = document.body.classList.contains("light-mode") ? "dark_mode" : "light_mode";

    const defaultText = `<div class="default-text">
                            <h1>رديّـة</h1>
                            <p>منصة تفاعلية لممارسة المحاورة الشعرية.
                              
                            <br> يمكنك إدخال بيت الشعر الخاص بك، وسيرد عليك النموذج في محاورة ممتعة</p>
                        </div>`;

    chatContainer.innerHTML = defaultText; // Set to default text since chats are cleared
    chatContainer.scrollTo(0, chatContainer.scrollHeight); // Scroll to bottom of the chat container
}


const createChatElement = (content, className) => {
    // Create new div and apply chat, specified class and set html content of div
    const chatDiv = document.createElement("div");
    chatDiv.classList.add("chat", className);
    chatDiv.innerHTML = content;
    return chatDiv; // Return the created chat div
}

const getChatResponse = async (incomingChatDiv) => { 
    const API_URL = "http://localhost:5000/api/chat";  // Updated endpoint to match Flask route
    const pElement = document.createElement("p");

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: userText })
        });

        if (!response.ok) {
            throw new Error("Network response was not ok");
        }

        const data = await response.json();
        pElement.textContent = data.response.trim();
    } catch (error) {
        pElement.classList.add("error");
        pElement.textContent = "Oops! Something went wrong while retrieving the response. Please try again.";
        console.error("Fetch error:", error);  // Log error to console for debugging
    }

    incomingChatDiv.querySelector(".typing-animation").remove();
    incomingChatDiv.querySelector(".chat-details").appendChild(pElement);
    localStorage.setItem("all-chats", chatContainer.innerHTML);
    chatContainer.scrollTo(0, chatContainer.scrollHeight);
}


const copyResponse = (copyBtn) => {
    // Copy the text content of the response to the clipboard
    const reponseTextElement = copyBtn.parentElement.querySelector("p");
    navigator.clipboard.writeText(reponseTextElement.textContent);
    copyBtn.textContent = "done";
    setTimeout(() => copyBtn.textContent = "content_copy", 1000);
}

const showTypingAnimation = () => {
    // Display the typing animation and call the getChatResponse function
    const html = `<div class="chat-content">
                    <div class="chat-details">
                        <img src="static/images/Redya Logo.png" alt="chatbot-img" style="width: 40px; height: auto;">
                        <div class="typing-animation">
                            <div class="typing-dot" style="--delay: 0.2s"></div>
                            <div class="typing-dot" style="--delay: 0.3s"></div>
                            <div class="typing-dot" style="--delay: 0.4s"></div>
                        </div>
                    </div>
                    <span onclick="copyResponse(this)" class="material-symbols-rounded">content_copy</span>
                </div>`;
    // Create an incoming chat div with typing animation and append it to chat container
    const incomingChatDiv = createChatElement(html, "incoming");
    chatContainer.appendChild(incomingChatDiv);
    chatContainer.scrollTo(0, chatContainer.scrollHeight);
    getChatResponse(incomingChatDiv);
}
const handleOutgoingChat = () => {
    userText = chatInput.value.trim(); // Get chatInput value and remove extra spaces
    if (!userText) return; // If chatInput is empty return from here

    // Clear the input field and reset its height
    chatInput.value = "";
    chatInput.style.height = `${initialInputHeight}px`;

    const html = `<div class="chat-content">
                    <div class="chat-details">
                        <img src="static/images/poet.png" alt="user-img">
                        <p>${userText}</p>
                    </div>
                </div>`;

    // Create an outgoing chat div with user's message and append it to chat container
    const outgoingChatDiv = createChatElement(html, "outgoing");

    // Remove the default text, if it exists
    chatContainer.querySelector(".default-text")?.remove();
    
    // Hide the background image by adding a class
    chatContainer.classList.add("hide-background");

    chatContainer.appendChild(outgoingChatDiv);
    chatContainer.scrollTo(0, chatContainer.scrollHeight);
    setTimeout(showTypingAnimation, 500);
}


deleteButton.addEventListener("click", () => {
    // Remove the chats from local storage and call loadDataFromLocalstorage function
    if(confirm("Are you sure you want to delete all the chats?")) {
        localStorage.removeItem("all-chats");
        loadDataFromLocalstorage();
        
        // Restore the background image by removing the hide-background class
        chatContainer.classList.remove("hide-background");
    }

});

themeButton.addEventListener("click", () => {
    // Toggle body's class for the theme mode and save the updated theme to the local storage 
    document.body.classList.toggle("light-mode");
    localStorage.setItem("themeColor", themeButton.innerText);
    themeButton.innerText = document.body.classList.contains("light-mode") ? "dark_mode" : "light_mode";
});

const initialInputHeight = chatInput.scrollHeight;

chatInput.addEventListener("input", () => {   
    // Adjust the height of the input field dynamically based on its content
    chatInput.style.height =  `${initialInputHeight}px`;
    chatInput.style.height = `${chatInput.scrollHeight}px`;
});

chatInput.addEventListener("keydown", (e) => {
    // If the Enter key is pressed without Shift and the window width is larger 
    // than 800 pixels, handle the outgoing chat
    if (e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
        e.preventDefault();
        handleOutgoingChat();
    }
});

loadDataFromLocalstorage();
sendButton.addEventListener("click", handleOutgoingChat);
