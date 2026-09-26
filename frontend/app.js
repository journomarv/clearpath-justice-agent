(() => {
  "use strict";

  const API_BASE =
    window.CLEARPATH_API_BASE ||
    "https://api.clearpathjustice.org.za";

  const input = document.querySelector(".input-wrapper input");
  const sendButton = document.querySelector(".input-wrapper button");
  const suggestionCards = document.querySelectorAll(".suggestion-card");
  const hero = document.querySelector(".hero");
  const inputArea = document.querySelector(".input-area");

  let sending = false;

  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function formatText(text) {
    return escapeHtml(text).replace(/\n/g, "<br>");
  }

  function setSending(state) {
    sending = state;

    if (sendButton) {
      sendButton.disabled = state;
      sendButton.style.opacity = state ? "0.5" : "1";
      sendButton.style.pointerEvents = state ? "none" : "auto";
    }

    if (input) {
      input.disabled = state;
    }
  }

  function createChatView() {
    let chatView = document.querySelector(".path-chat-view");

    if (chatView) {
      return chatView;
    }

    chatView = document.createElement("div");
    chatView.className = "path-chat-view";

    chatView.innerHTML = `
      <div class="path-chat-messages" id="pathChatMessages"></div>
    `;

    hero.insertBefore(chatView, inputArea);

    return chatView;
  }

  function addMessage(role, text) {
    const chatView = createChatView();
    const messages = chatView.querySelector("#pathChatMessages");

    const message = document.createElement("div");

    message.className =
      role === "user"
        ? "path-message path-message-user"
        : "path-message path-message-assistant";

    message.innerHTML = `
      <div class="path-message-label">
        ${role === "user" ? "You" : "Path"}
      </div>
      <div class="path-message-content">
        ${formatText(text)}
      </div>
    `;

    messages.appendChild(message);

    message.scrollIntoView({
      behavior: "smooth",
      block: "nearest"
    });

    return message;
  }

  function addTypingMessage() {
    const chatView = createChatView();
    const messages = chatView.querySelector("#pathChatMessages");

    const message = document.createElement("div");

    message.className =
      "path-message path-message-assistant";

    message.id = "pathTypingMessage";

    message.innerHTML = `
      <div class="path-message-label">Path</div>
      <div class="path-message-content path-thinking">
        <span></span>
        <span></span>
        <span></span>
      </div>
    `;

    messages.appendChild(message);

    message.scrollIntoView({
      behavior: "smooth",
      block: "nearest"
    });
  }

  function removeTypingMessage() {
    const message =
      document.querySelector("#pathTypingMessage");

    if (message) {
      message.remove();
    }
  }

  function addMetadata(data) {
    if (!data) {
      return "";
    }

    let html = "";

    if (data.relief_type) {
      html += `
        <div class="path-metadata">
          <strong>Relief type:</strong>
          ${escapeHtml(data.relief_type)}
        </div>
      `;
    }

    if (data.next_action) {
      html += `
        <div class="path-metadata">
          <strong>Next action:</strong>
          ${escapeHtml(data.next_action)}
        </div>
      `;
    }

    if (data.requires_human) {
      html += `
        <div class="path-metadata">
          A ClearPath team member may need to review this.
        </div>
      `;
    }

    return html;
  }

  function addAssistantResponse(data) {
    const chatView = createChatView();
    const messages = chatView.querySelector("#pathChatMessages");

    const message = document.createElement("div");

    message.className =
      "path-message path-message-assistant";

    const answer =
      data?.message ||
      "I wasn't able to generate a response.";

    message.innerHTML = `
      <div class="path-message-label">Path</div>
      <div class="path-message-content">
        ${formatText(answer)}
      </div>
      ${addMetadata(data)}
    `;

    messages.appendChild(message);

    message.scrollIntoView({
      behavior: "smooth",
      block: "nearest"
    });
  }

  async function sendMessage(value) {
    const message = String(value || "").trim();

    if (!message || sending) {
      return;
    }

    setSending(true);

    addMessage("user", message);
    addTypingMessage();

    if (input) {
      input.value = "";
    }

    try {
      const response = await fetch(
        API_BASE + "/chat",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Accept": "application/json"
          },
          body: JSON.stringify({
            message: message,
            relief_type_hint: null
          })
        }
      );

      let data = null;

      try {
        data = await response.json();
      } catch {
        data = null;
      }

      removeTypingMessage();

      if (!response.ok) {
        throw new Error(
          data?.detail ||
          "Path could not process that request right now."
        );
      }

      addAssistantResponse(data);
    } catch (error) {
      removeTypingMessage();

      addMessage(
        "assistant",
        error?.message ||
        "Something went wrong while connecting to Path."
      );
    } finally {
      setSending(false);

      if (input) {
        input.focus();
      }
    }
  }

  if (sendButton) {
    sendButton.addEventListener("click", () => {
      sendMessage(input?.value);
    });
  }

  if (input) {
    input.addEventListener("keydown", (event) => {
      if (
        event.key === "Enter" &&
        !event.shiftKey
      ) {
        event.preventDefault();
        sendMessage(input.value);
      }
    });

    input.addEventListener("input", () => {
      if (sendButton) {
        sendButton.disabled =
          !input.value.trim() || sending;
      }
    });
  }

  suggestionCards.forEach((card) => {
    card.addEventListener("click", () => {
      const text =
        card.querySelector("span:last-child")
          ?.textContent
          ?.trim();

      if (text) {
        sendMessage(text);
      }
    });
  });

  if (input) {
    input.addEventListener("focus", () => {
      if (sendButton) {
        sendButton.disabled =
          !input.value.trim() || sending;
      }
    });
  }

  fetch(API_BASE + "/health", {
    method: "GET",
    headers: {
      "Accept": "application/json"
    }
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Health check failed");
      }

      document.body.classList.add("path-online");
    })
    .catch(() => {
      document.body.classList.add("path-offline");
    });
})();
