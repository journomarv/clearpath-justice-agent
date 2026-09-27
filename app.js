const API_BASE_URL = "https://api.clearpathjustice.org.za";

const main = document.querySelector("#main");
const installBtn = document.querySelector("#installBtn");

let deferredInstallPrompt = null;
let isSending = false;

const state = {
  messages: [
    {
      role: "assistant",
      text: "Hello. I’m Path. Tell me what happened, and I’ll help you understand what options may be available."
    }
  ]
};

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderHome() {
  main.innerHTML = `
    <section class="hero">
      <p class="eyebrow">ClearPath Justice</p>
      <h1>A conversation about justice.</h1>
      <p>
        Tell Path what happened. Get help understanding your possible
        justice pathway and what you can do next.
      </p>
      <a class="primary-button" href="#path">Talk to Path</a>
    </section>

    <section class="card">
      <h2>Justice should be navigable.</h2>
      <p>
        ClearPath helps people understand processes, prepare for next steps,
        manage their journey and connect with appropriate human support.
      </p>
    </section>
  `;
}

function renderPath() {
  main.innerHTML = `
    <section>
      <p class="eyebrow">Path</p>
      <h2>Tell Path what happened.</h2>
      <p>
        Start with your situation in your own words.
      </p>

      <div class="chat" id="chat" aria-live="polite"></div>

      <form class="chat-form" id="chatForm">
        <textarea id="messageInput"
          placeholder="Tell Path what happened..."
          aria-label="Message Path"
          required
          ${isSending ? "disabled" : ""}></textarea>

        <button class="send-button" type="submit" ${isSending ? "disabled" : ""}>
          ${isSending ? "Sending…" : "Send"}
        </button>
      </form>
    </section>
  `;

  renderMessages();

  document.querySelector("#chatForm")
    ?.addEventListener("submit", handleMessage);
}

function renderMessages() {
  const chat = document.querySelector("#chat");

  if (!chat) return;

  chat.innerHTML = state.messages
    .map(message => {
      let html = `
        <div class="message ${escapeHtml(message.role)}">
          ${escapeHtml(message.text)}
        </div>
      `;

      if (message.next_action) {
        html += `
          <div class="message-meta">
            Next step: ${escapeHtml(formatNextAction(message.next_action))}
          </div>
        `;
      }

      if (message.sources?.length) {
        html += `
          <div class="sources">
            <strong>Sources</strong>
            ${message.sources.map(source => `
              <div class="source-item">
                ${
                  source.url
                    ? `<a href="${escapeHtml(source.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(source.title)}</a>`
                    : `<span>${escapeHtml(source.title)}</span>`
                }
              </div>
            `).join("")}
          </div>
        `;
      }

      return html;
    })
    .join("");

  chat.scrollTop = chat.scrollHeight;
}

function formatNextAction(action) {
  return String(action)
    .replaceAll("_", " ")
    .replace(/\b\w/g, letter => letter.toUpperCase());
}

async function sendToPath(message) {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      message
    })
  });

  let data = null;

  try {
    data = await response.json();
  } catch {
    throw new Error("Path returned an invalid response.");
  }

  if (!response.ok) {
    const detail = data?.detail;

    if (Array.isArray(detail)) {
      throw new Error(
        detail
          .map(item => item?.msg || "The message could not be processed.")
          .join(" ")
      );
    }

    throw new Error(
      detail || "Path could not process your message right now."
    );
  }

  return data;
}

async function handleMessage(event) {
  event.preventDefault();

  if (isSending) return;

  const input = document.querySelector("#messageInput");
  const text = input?.value.trim();

  if (!text) return;

  state.messages.push({
    role: "user",
    text
  });

  isSending = true;
  renderPath();

  try {
    const data = await sendToPath(text);

    state.messages.push({
      role: "assistant",
      text: data.message || "Path did not return a message.",
      next_action: data.next_action,
      requires_human: data.requires_human,
      confidence: data.confidence,
      sources: data.sources || [],
      relief_type: data.relief_type
    });
  } catch (error) {
    console.error("Path API error:", error);

    state.messages.push({
      role: "assistant",
      text: error.message ||
        "I couldn't connect to Path right now. Please try again."
    });
  } finally {
    isSending = false;
    renderPath();
  }
}

function renderJourney() {
  main.innerHTML = `
    <section>
      <p class="eyebrow">Your journey</p>
      <h2>Understand where you are.</h2>
      <p>
        Assess → Prepare → Manage → Refer → Verify.
      </p>

      <div class="list">
        <div class="list-item">
          <strong>Assess</strong>
          <span>Understand whether a pathway may apply.</span>
        </div>
        <div class="list-item">
          <strong>Prepare</strong>
          <span>Identify information and documents that may be required.</span>
        </div>
        <div class="list-item">
          <strong>Manage</strong>
          <span>Keep track of your justice journey.</span>
        </div>
        <div class="list-item">
          <strong>Refer</strong>
          <span>Connect with appropriate human support.</span>
        </div>
        <div class="list-item">
          <strong>Verify</strong>
          <span>Record the outcome while minimising unnecessary disclosure.</span>
        </div>
      </div>
    </section>
  `;
}

function renderMore() {
  main.innerHTML = `
    <section>
      <p class="eyebrow">ClearPath Justice</p>
      <h2>More</h2>

      <div class="list">
        <div class="list-item">
          <strong>About ClearPath</strong>
          <span>Digital infrastructure for navigating justice pathways.</span>
        </div>

        <div class="list-item">
          <strong>AI assists, not adjudicates.</strong>
          <span>Path helps people understand and navigate processes.</span>
        </div>
      </div>
    </section>
  `;
}

function router() {
  const route = window.location.hash.replace("#", "") || "home";

  document.querySelectorAll(".app-navigation a").forEach(link => {
    link.classList.toggle("active", link.dataset.route === route);
  });

  if (route === "path") {
    renderPath();
  } else if (route === "journey") {
    renderJourney();
  } else if (route === "more") {
    renderMore();
  } else {
    renderHome();
  }
}

window.addEventListener("hashchange", router);

window.addEventListener("beforeinstallprompt", event => {
  event.preventDefault();
  deferredInstallPrompt = event;
  installBtn.hidden = false;
});

installBtn?.addEventListener("click", async () => {
  if (!deferredInstallPrompt) return;

  deferredInstallPrompt.prompt();
  await deferredInstallPrompt.userChoice;

  deferredInstallPrompt = null;
  installBtn.hidden = true;
});

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js").catch(console.error);
  });
}

router();
