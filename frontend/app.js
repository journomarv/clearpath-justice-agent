(() => {
  "use strict";

  const API_BASE =
    window.CLEARPATH_API_BASE ||
    "https://api.clearpathjustice.org.za";

  const $ = (id) => document.getElementById(id);

  const chatForm = $("chatForm");
  const messageInput = $("messageInput");
  const sendButton = $("sendButton");
  const messages = $("messages");
  const welcome = $("welcome");

  const statusDot = $("statusDot");
  const statusText = $("statusText");

  const newChatButton = $("newChatButton");
  const aboutButton = $("aboutButton");
  const infoButton = $("infoButton");
  const aboutModal = $("aboutModal");
  const closeModal = $("closeModal");

  const mobileMenuButton = $("mobileMenuButton");
  const sidebar = $("sidebar");

  let sending = false;


  /* ---------------------------------------------------------
     Utilities
  --------------------------------------------------------- */

  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }


  function formatText(text) {
    let html = escapeHtml(text);

    html = html.replace(
      /\*\*(.+?)\*\*/g,
      "<strong>$1</strong>"
    );

    html = html.replace(
      /`([^`]+)`/g,
      "<code>$1</code>"
    );

    html = html.replace(
      /\n/g,
      "<br>"
    );

    return html;
  }


  function scrollToBottom() {
    const container = $("chatContainer");

    if (container) {
      container.scrollTop = container.scrollHeight;
    }

    window.scrollTo({
      top: document.body.scrollHeight,
      behavior: "smooth"
    });
  }


  function setStatus(state, text) {
    statusDot.className = "status-dot";

    if (state) {
      statusDot.classList.add(state);
    }

    statusText.textContent = text;
  }


  /* ---------------------------------------------------------
     Health check
  --------------------------------------------------------- */

  async function checkHealth() {
    try {
      const response = await fetch(`${API_BASE}/health`, {
        method: "GET",
        headers: {
          Accept: "application/json"
        }
      });

      if (!response.ok) {
        throw new Error("Health check failed");
      }

      setStatus("online", "Path online");
    } catch (error) {
      console.error("Health check:", error);
      setStatus("offline", "Path unavailable");
    }
  }


  /* ---------------------------------------------------------
     Messages
  --------------------------------------------------------- */

  function addUserMessage(text) {
    const wrapper = document.createElement("div");

    wrapper.className = "message message-user";

    wrapper.innerHTML = `
      <div class="message-content">
        ${formatText(text)}
      </div>
    `;

    messages.appendChild(wrapper);

    scrollToBottom();
  }


  function addAssistantMessage(data) {
    const wrapper = document.createElement("div");

    wrapper.className = "message message-assistant";

    const answer =
      data?.answer ||
      "I wasn't able to generate a response.";

    let metadata = "";

    if (data?.pathway) {
      metadata += `
        <span class="message-meta-item">
          ${escapeHtml(formatPathway(data.pathway))}
        </span>
      `;
    }

    if (data?.next_step) {
      metadata += `
        <div class="next-step">
          <strong>Next step</strong>
          <span>${formatText(data.next_step)}</span>
        </div>
      `;
    }

    if (data?.uncertainty) {
      metadata += `
        <div class="uncertainty">
          ${formatText(data.uncertainty)}
        </div>
      `;
    }

    wrapper.innerHTML = `
      <div class="assistant-mark">P</div>

      <div class="assistant-body">

        <div class="assistant-name">
          Path
        </div>

        <div class="message-content">
          ${formatText(answer)}
        </div>

        ${
          metadata
            ? `<div class="message-metadata">${metadata}</div>`
            : ""
        }

      </div>
    `;

    messages.appendChild(wrapper);

    scrollToBottom();
  }


  function addErrorMessage(message) {
    const wrapper = document.createElement("div");

    wrapper.className =
      "message message-assistant message-error";

    wrapper.innerHTML = `
      <div class="assistant-mark">P</div>

      <div class="assistant-body">

        <div class="assistant-name">
          Path
        </div>

        <div class="message-content">
          ${formatText(message)}
        </div>

      </div>
    `;

    messages.appendChild(wrapper);

    scrollToBottom();
  }


  function addTypingIndicator() {
    const wrapper = document.createElement("div");

    wrapper.className =
      "message message-assistant typing-message";

    wrapper.id = "typingIndicator";

    wrapper.innerHTML = `
      <div class="assistant-mark">P</div>

      <div class="assistant-body">

        <div class="assistant-name">
          Path
        </div>

        <div class="typing-indicator">
          <span></span>
          <span></span>
          <span></span>
        </div>

      </div>
    `;

    messages.appendChild(wrapper);

    scrollToBottom();
  }


  function removeTypingIndicator() {
    const indicator = $("typingIndicator");

    if (indicator) {
      indicator.remove();
    }
  }


  function formatPathway(pathway) {
    const names = {
      general_expungement: "General expungement",
      cannabis_related_relief: "Cannabis-related relief",
      child_justice: "Child justice",
      police_clearance: "Police clearance",
      application_prep: "Application preparation",
      tracking: "Application tracking",
      post_decision: "After a decision"
    };

    return names[pathway] || pathway;
  }


  /* ---------------------------------------------------------
     Chat
  --------------------------------------------------------- */

  async function sendMessage(text) {
    const message = String(text || "").trim();

    if (!message || sending) {
      return;
    }

    sending = true;

    messageInput.value = "";
    autoResize();

    sendButton.disabled = true;

    if (welcome) {
      welcome.classList.add("hidden");
    }

    addUserMessage(message);
    addTypingIndicator();

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json"
        },
        body: JSON.stringify({
          message,
          pathway: null
        })
      });

      let data = null;

      try {
        data = await response.json();
      } catch {
        data = null;
      }

      if (!response.ok) {
        const detail =
          data?.detail ||
          "Path could not process that request right now.";

        throw new Error(detail);
      }

      removeTypingIndicator();
      addAssistantMessage(data);

      setStatus("online", "Path online");

    } catch (error) {
      console.error("Chat error:", error);

      removeTypingIndicator();

      addErrorMessage(
        error?.message ||
        "Something went wrong while connecting to Path."
      );

      setStatus("offline", "Connection issue");

    } finally {
      sending = false;

      updateSendButton();
      messageInput.focus();
    }
  }


  /* ---------------------------------------------------------
     Composer
  --------------------------------------------------------- */

  function updateSendButton() {
    sendButton.disabled =
      sending ||
      !messageInput.value.trim();
  }


  function autoResize() {
    messageInput.style.height = "auto";

    const maxHeight = 180;

    messageInput.style.height =
      `${Math.min(messageInput.scrollHeight, maxHeight)}px`;
  }


  chatForm.addEventListener("submit", (event) => {
    event.preventDefault();

    sendMessage(messageInput.value);
  });


  messageInput.addEventListener("input", () => {
    autoResize();
    updateSendButton();
  });


  messageInput.addEventListener("keydown", (event) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();

      if (!sendButton.disabled) {
        chatForm.requestSubmit();
      }
    }
  });


  /* ---------------------------------------------------------
     Starter prompts
  --------------------------------------------------------- */

  document
    .querySelectorAll(".starter-card")
    .forEach((card) => {
      card.addEventListener("click", () => {
        const prompt =
          card.dataset.prompt || "";

        sendMessage(prompt);
      });
    });


  /* ---------------------------------------------------------
     New chat
  --------------------------------------------------------- */

  function resetChat() {
    messages.innerHTML = "";

    if (welcome) {
      welcome.classList.remove("hidden");
    }

    messageInput.value = "";

    autoResize();
    updateSendButton();

    messageInput.focus();

    closeSidebar();
  }


  newChatButton.addEventListener(
    "click",
    resetChat
  );


  /* ---------------------------------------------------------
     About modal
  --------------------------------------------------------- */

  function openModal() {
    aboutModal.hidden = false;

    document.body.classList.add(
      "modal-open"
    );
  }


  function closeAboutModal() {
    aboutModal.hidden = true;

    document.body.classList.remove(
      "modal-open"
    );
  }


  aboutButton.addEventListener(
    "click",
    openModal
  );

  infoButton.addEventListener(
    "click",
    openModal
  );

  closeModal.addEventListener(
    "click",
    closeAboutModal
  );


  aboutModal.addEventListener(
    "click",
    (event) => {
      if (event.target === aboutModal) {
        closeAboutModal();
      }
    }
  );


  document.addEventListener(
    "keydown",
    (event) => {
      if (event.key === "Escape") {
        closeAboutModal();
        closeSidebar();
      }
    }
  );


  /* ---------------------------------------------------------
     Mobile sidebar
  --------------------------------------------------------- */

  function openSidebar() {
    sidebar.classList.add("open");
    document.body.classList.add("sidebar-open");
  }


  function closeSidebar() {
    sidebar.classList.remove("open");
    document.body.classList.remove("sidebar-open");
  }


  mobileMenuButton.addEventListener(
    "click",
    () => {
      if (sidebar.classList.contains("open")) {
        closeSidebar();
      } else {
        openSidebar();
      }
    }
  );


  /* ---------------------------------------------------------
     Initialisation
  --------------------------------------------------------- */

  autoResize();
  updateSendButton();
  checkHealth();

  messageInput.focus();

})();
