let target = document.getElementById("targetUser").value;
let ws;

function connect() {
    // Gunakan 'wss://' jika halaman pakai HTTPS
    const protocol = location.protocol === "https:" ? "wss" : "ws";
    ws = new WebSocket(`${protocol}://${location.host}/ws/${target}`);

    const chatBox = document.getElementById("chat-box");
    chatBox.innerHTML = "";

    ws.onmessage = function(event) {
        const text = event.data;
        const msgDiv = document.createElement("div");
        msgDiv.classList.add("chat-message");

        const sender = text.match(/\[(.*?)\]/)?.[1] || "??";
        msgDiv.classList.add(sender === username ? "me" : "other");
        msgDiv.textContent = text;
        chatBox.appendChild(msgDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    };

    ws.onclose = () => {
        console.warn("WebSocket closed, attempting reconnect in 3s...");
        setTimeout(connect, 3000); // auto reconnect jika perlu
    };
}

function switchTarget(newTarget) {
    target = newTarget;
    if (ws.readyState === WebSocket.OPEN) {
        ws.close();
    }
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
