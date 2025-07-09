let target = document.getElementById("targetUser").value;
let ws;

function connect() {
    ws = new WebSocket(`ws://${location.host}/ws/${target}`);
    const chatBox = document.getElementById("chat-box");
    chatBox.innerHTML = "";

    ws.onmessage = function(event) {
        const text = event.data;
        const msgDiv = document.createElement("div");
        msgDiv.classList.add("chat-message");

        const sender = text.match(/\\[(.*?)\\]/)?.[1] || "??";
        msgDiv.classList.add(sender === username ? "me" : "other");
        msgDiv.textContent = text;
        chatBox.appendChild(msgDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    };
}

function switchTarget(newTarget) {
    target = newTarget;
    ws.close();
    connect();
}

function sendMessage() {
    const input = document.getElementById("messageInput");
    if (input.value.trim() !== "") {
        ws.send(input.value.trim());
        input.value = "";
    }
}

document.getElementById("messageInput").addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendMessage();
});

connect();
