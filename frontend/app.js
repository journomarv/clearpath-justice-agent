const API_BASE = "https://api.clearpathjustice.org.za";

const welcomeScreen = document.getElementById("welcomeScreen");
const chatScreen = document.getElementById("chatScreen");
const messages = document.getElementById("messages");

const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");

const newChatButton = document.getElementById("newChatButton");
const mobileNewChat = document.getElementById("mobileNewChat");

const statusDot = document.getElementById("statusDot");
const statusText = document.getElementById("statusText");

let currentPathway = null;
let isSending = false;


/* -------------------------------------------------
   HEALTH CHECK
------------------------------------------------- */

async function checkHealth() {

    try {

        const response = await fetch(`${API_BASE}/health`, {
            method: "GET"
        });

        if (!response.ok) {
            throw new Error("Health check failed");
        }

        statusDot.classList.add("online");
        statusDot.classList.remove("offline");

        statusText.textContent = "Service online";

    } catch (error) {

        statusDot.classList.remove("online");
        statusDot.classList.add("offline");

        statusText.textContent = "Service unavailable";

        console.error("Health check:", error);
    }
}


/* -------------------------------------------------
   START NEW CHAT
------------------------------------------------- */

function startNewChat() {

    messages.innerHTML = "";

    currentPathway = null;

    chatScreen.classList.add("hidden");
    welcomeScreen.classList.remove("hidden");

    messageInput.value = "";

    autoResize();

    messageInput.focus();
}


newChatButton.addEventListener("click", startNewChat);
mobileNewChat.addEventListener("click", startNewChat);


/* -------------------------------------------------
   QUICK ACTIONS
------------------------------------------------- */

document.querySelectorAll("[data-prompt]").forEach(button => {

    button.addEventListener("click", () => {

        const prompt = button.dataset.prompt;

        messageInput.value = prompt;

        autoResize();

        sendMessage(prompt);
    });

});


/* -------------------------------------------------
   TEXTAREA
------------------------------------------------- */

messageInput.addEventListener("input", autoResize);

function autoResize() {

    messageInput.style.height = "auto";

    messageInput.style.height =
        Math.min(messageInput.scrollHeight, 180) + "px";
}


messageInput.addEventListener("keydown", event => {

    if (event.key === "Enter" && !event.shiftKey) {

        event.preventDefault();

        chatForm.requestSubmit();
    }

});


/* -------------------------------------------------
   FORM
------------------------------------------------- */

chatForm.addEventListener("submit", async event => {

    event.preventDefault();

    const message = messageInput.value.trim();

    if (!message || isSending) {
        return;
    }

    await sendMessage(message);
});


/* -------------------------------------------------
   SEND MESSAGE
------------------------------------------------- */

async function sendMessage(message) {

    if (!message || isSending) {
        return;
    }

    isSending = true;

    sendButton.disabled = true;

    showChat();

    addUserMessage(message);

    messageInput.value = "";

    autoResize();

    const typingElement = addTypingIndicator();

    try {

        const response = await fetch(`${API_BASE}/chat`, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: message,
                pathway: currentPathway
            })

        });


        const data = await response.json();


        if (!response.ok) {

            const detail =
                data?.detail ||
                "The ClearPath Justice service could not process your request.";

            throw new Error(detail);
        }


        if (typingElement) {
            typingElement.remove();
        }


        currentPathway =
            data.pathway ||
            currentPathway;


        addAssistantMessage(data);


    } catch (error) {

        if (typingElement) {
            typingElement.remove();
        }

        addErrorMessage(error);

        console.error("Chat error:", error);

    } finally {

        isSending = false;

        sendButton.disabled = false;

        messageInput.focus();
    }
}


/* -------------------------------------------------
   SHOW CHAT
------------------------------------------------- */

function showChat() {

    welcomeScreen.classList.add("hidden");

    chatScreen.classList.remove("hidden");
}


/* -------------------------------------------------
   USER MESSAGE
------------------------------------------------- */

function addUserMessage(text) {

    const wrapper = document.createElement("div");

    wrapper.className = "message user";


    const content = document.createElement("div");

    content.className = "message-content";

    content.textContent = text;


    wrapper.appendChild(content);

    messages.appendChild(wrapper);

    scrollToBottom();
}


/* -------------------------------------------------
   ASSISTANT MESSAGE
------------------------------------------------- */

function addAssistantMessage(data) {

    const wrapper = document.createElement("div");

    wrapper.className = "message assistant";


    const inner = document.createElement("div");

    inner.className = "message-content";


    const meta = document.createElement("div");

    meta.className = "assistant-meta";


    const mark = document.createElement("span");

    mark.className = "assistant-mark";

    mark.textContent = "C";


    const label = document.createElement("span");

    label.textContent = "ClearPath Justice";


    meta.appendChild(mark);

    meta.appendChild(label);


    inner.appendChild(meta);


    const answer = document.createElement("div");

    answer.innerHTML = formatResponse(data.answer || "");

    inner.appendChild(answer);


    /* RESPONSE INFORMATION */

    const info = document.createElement("div");

    info.className = "response-info";


    if (data.pathway) {

        const pathway = document.createElement("span");

        pathway.className = "pathway";

        pathway.textContent =
            formatPathway(data.pathway);

        info.appendChild(pathway);
    }


    if (
        Array.isArray(data.knowledge_sources) &&
        data.knowledge_sources.length > 0
    ) {

        const sources = document.createElement("div");

        sources.textContent =
            "Information considered: " +
            data.knowledge_sources.join(", ");

        info.appendChild(sources);
    }


    if (data.next_step) {

        const nextStep = document.createElement("div");

        nextStep.className = "next-step";

        nextStep.innerHTML =
            "<strong>Possible next step:</strong> " +
            escapeHtml(data.next_step);

        info.appendChild(nextStep);
    }


    if (data.uncertainty) {

        const uncertainty = document.createElement("div");

        uncertainty.className = "uncertainty";

        uncertainty.innerHTML =
            "<strong>Important:</strong> " +
            escapeHtml(data.uncertainty);

        info.appendChild(uncertainty);
    }


    if (info.children.length > 0) {
        inner.appendChild(info);
    }


    wrapper.appendChild(inner);

    messages.appendChild(wrapper);

    scrollToBottom();
}


/* -------------------------------------------------
   ERROR MESSAGE
------------------------------------------------- */

function addErrorMessage(error) {

    const wrapper = document.createElement("div");

    wrapper.className = "message assistant";


    const content = document.createElement("div");

    content.className =
        "message-content error-message";


    content.innerHTML = `
        <strong>Something went wrong.</strong>
        <br>
        ${escapeHtml(
            error.message ||
            "Please try again in a moment."
        )}
    `;


    wrapper.appendChild(content);

    messages.appendChild(wrapper);

    scrollToBottom();
}


/* -------------------------------------------------
   TYPING INDICATOR
------------------------------------------------- */

function addTypingIndicator() {

    const wrapper = document.createElement("div");

    wrapper.className = "message assistant";


    const content = document.createElement("div");

    content.className = "message-content";


    const meta = document.createElement("div");

    meta.className = "assistant-meta";


    const mark = document.createElement("span");

    mark.className = "assistant-mark";

    mark.textContent = "C";


    const label = document.createElement("span");

    label.textContent = "ClearPath Justice";


    meta.appendChild(mark);

    meta.appendChild(label);


    const typing = document.createElement("div");

    typing.className = "typing";

    typing.innerHTML = `
        <span></span>
        <span></span>
        <span></span>
    `;


    content.appendChild(meta);

    content.appendChild(typing);

    wrapper.appendChild(content);

    messages.appendChild(wrapper);

    scrollToBottom();

    return wrapper;
}


/* -------------------------------------------------
   RESPONSE FORMATTING
------------------------------------------------- */

function formatResponse(text) {

    let safe = escapeHtml(text);

    safe = safe.replace(
        /\*\*(.*?)\*\*/g,
        "<strong>$1</strong>"
    );

    safe = safe.replace(
        /\n\n/g,
        "<br><br>"
    );

    safe = safe.replace(
        /\n/g,
        "<br>"
    );

    return safe;
}


function escapeHtml(text) {

    const div = document.createElement("div");

    div.textContent = text;

    return div.innerHTML;
}


/* -------------------------------------------------
   PATHWAY
------------------------------------------------- */

function formatPathway(pathway) {

    if (!pathway) {
        return "";
    }

    return pathway
        .replace(/_/g, " ")
        .replace(/\b\w/g, letter => letter.toUpperCase());
}


/* -------------------------------------------------
   SCROLL
------------------------------------------------- */

function scrollToBottom() {

    requestAnimationFrame(() => {

        chatScreen.scrollTop =
            chatScreen.scrollHeight;

        window.scrollTo({
            top: document.body.scrollHeight,
            behavior: "smooth"
        });

    });
}


/* -------------------------------------------------
   INITIALISE
------------------------------------------------- */

checkHealth();
