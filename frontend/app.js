/* =========================================================
   ClearPath Justice — Path
   Conversation frontend
   ========================================================= */

const conversation = document.getElementById("conversation");
const welcome = document.getElementById("welcome");
const messages = document.getElementById("messages");

const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");

const backButton = document.getElementById("backButton");
const infoButton = document.getElementById("infoButton");
const addButton = document.getElementById("addButton");

const aboutModal = document.getElementById("aboutModal");
const closeModal = document.getElementById("closeModal");

let isSending = false;


/* ---------------------------------------------------------
   API configuration
   --------------------------------------------------------- */

/*
 * Because the frontend is served by the same FastAPI
 * application, using "/chat" keeps the frontend portable.
 *
 * If your deployed backend uses a different API domain,
 * change this to the full endpoint.
 */
const CHAT_ENDPOINT = "/chat";


/* ---------------------------------------------------------
   Utility functions
   --------------------------------------------------------- */

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


function scrollToBottom() {
    requestAnimationFrame(() => {
        conversation.scrollTo({
            top: conversation.scrollHeight,
            behavior: "smooth"
        });
    });
}


function resizeInput() {
    messageInput.style.height = "auto";

    const newHeight = Math.min(
        messageInput.scrollHeight,
        180
    );

    messageInput.style.height = `${newHeight}px`;
}


function updateSendButton() {
    const hasText = messageInput.value.trim().length > 0;

    sendButton.disabled = !hasText || isSending;
}


/* ---------------------------------------------------------
   Conversation state
   --------------------------------------------------------- */

function startConversation() {
    welcome.style.display = "none";
    messages.classList.add("active");
}


function addMessage(role, text) {
    startConversation();

    const message = document.createElement("article");
    message.className = `message ${role}`;

    const label =
        role === "user"
            ? "You"
            : "Path";

    message.innerHTML = `
        <div class="message-label">${label}</div>
        <div class="message-bubble">${escapeHtml(text)}</div>
    `;

    messages.appendChild(message);

    scrollToBottom();

    return message;
}


function addTypingIndicator() {
    startConversation();

    const message = document.createElement("article");
    message.className = "message assistant";
    message.id = "typingMessage";

    message.innerHTML = `
        <div class="message-label">Path</div>
        <div class="message-bubble">
            <div class="typing" aria-label="Path is thinking">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;

    messages.appendChild(message);

    scrollToBottom();
}


function removeTypingIndicator() {
    const typing = document.getElementById("typingMessage");

    if (typing) {
        typing.remove();
    }
}


/* ---------------------------------------------------------
   Response parsing
   --------------------------------------------------------- */

function extractResponse(data) {
    if (!data) {
        return "";
    }

    /*
     * Common response formats supported:
     *
     * { "response": "..." }
     * { "message": "..." }
     * { "answer": "..." }
     * { "content": "..." }
     * { "reply": "..." }
     */

    if (typeof data === "string") {
        return data;
    }

    const possibleFields = [
        "response",
        "message",
        "answer",
        "content",
        "reply",
        "text"
    ];

    for (const field of possibleFields) {
        if (
            typeof data[field] === "string" &&
            data[field].trim()
        ) {
            return data[field];
        }
    }

    /*
     * Some APIs return:
     *
     * { "data": { "response": "..." } }
     */

    if (data.data && typeof data.data === "object") {
        return extractResponse(data.data);
    }

    /*
     * OpenAI-style / agent-style response:
     *
     * { choices: [{ message: { content: "..." } }] }
     */

    if (
        Array.isArray(data.choices) &&
        data.choices.length > 0
    ) {
        const choice = data.choices[0];

        if (
            choice &&
            choice.message &&
            typeof choice.message.content === "string"
        ) {
            return choice.message.content;
        }

        if (
            choice &&
            typeof choice.text === "string"
        ) {
            return choice.text;
        }
    }

    return "";
}


/* ---------------------------------------------------------
   Send message
   --------------------------------------------------------- */

async function sendMessage(messageText) {
    const text = messageText.trim();

    if (!text || isSending) {
        return;
    }

    isSending = true;
    updateSendButton();

    addMessage("user", text);

    messageInput.value = "";
    resizeInput();

    addTypingIndicator();

    try {
        const response = await fetch(CHAT_ENDPOINT, {
            method: "POST",

            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },

            body: JSON.stringify({
                message: text
            })
        });


        let data = null;

        try {
            data = await response.json();
        } catch {
            data = null;
        }


        if (!response.ok) {
            let errorMessage =
                "I couldn't process that request right now.";

            if (data) {
                const serverError =
                    data.detail ||
                    data.error ||
                    data.message;

                if (typeof serverError === "string") {
                    errorMessage = serverError;
                }
            }

            throw new Error(errorMessage);
        }


        const answer = extractResponse(data);

        if (!answer) {
            throw new Error(
                "The server responded, but Path did not return an answer."
            );
        }

        removeTypingIndicator();

        addMessage("assistant", answer);

    } catch (error) {
        console.error("Path chat error:", error);

        removeTypingIndicator();

        addMessage(
            "assistant",
            `I'm having trouble connecting right now. ${error.message}`
        );

    } finally {
        isSending = false;
        updateSendButton();

        messageInput.focus();
    }
}


/* ---------------------------------------------------------
   Form submission
   --------------------------------------------------------- */

chatForm.addEventListener("submit", (event) => {
    event.preventDefault();

    sendMessage(messageInput.value);
});


/* ---------------------------------------------------------
   Textarea behaviour
   --------------------------------------------------------- */

messageInput.addEventListener("input", () => {
    resizeInput();
    updateSendButton();
});


messageInput.addEventListener("keydown", (event) => {
    /*
     * Enter sends.
     * Shift + Enter creates a new line.
     */

    if (
        event.key === "Enter" &&
        !event.shiftKey &&
        !event.isComposing
    ) {
        event.preventDefault();

        if (!sendButton.disabled) {
            sendMessage(messageInput.value);
        }
    }
});


/* ---------------------------------------------------------
   Suggested prompts
   --------------------------------------------------------- */

document.querySelectorAll(".suggestion").forEach((button) => {
    button.addEventListener("click", () => {
        const prompt = button.dataset.prompt;

        if (!prompt) {
            return;
        }

        messageInput.value = prompt;

        resizeInput();
        updateSendButton();

        messageInput.focus();

        /*
         * Send immediately when a suggested question is selected.
         */
        sendMessage(prompt);
    });
});


/* ---------------------------------------------------------
   Back button
   --------------------------------------------------------- */

backButton.addEventListener("click", () => {
    /*
     * If there is a conversation, return to the welcome state.
     * Otherwise use browser history where available.
     */

    if (messages.classList.contains("active")) {
        messages.innerHTML = "";
        messages.classList.remove("active");

        welcome.style.display = "";

        messageInput.value = "";
        resizeInput();
        updateSendButton();

        return;
    }

    if (window.history.length > 1) {
        window.history.back();
    }
});


/* ---------------------------------------------------------
   About modal
   --------------------------------------------------------- */

function openModal() {
    aboutModal.hidden = false;
    document.body.style.overflow = "hidden";
}


function closeAboutModal() {
    aboutModal.hidden = true;
    document.body.style.overflow = "";
}


infoButton.addEventListener("click", openModal);
closeModal.addEventListener("click", closeAboutModal);


aboutModal.addEventListener("click", (event) => {
    if (event.target === aboutModal) {
        closeAboutModal();
    }
});


document.addEventListener("keydown", (event) => {
    if (
        event.key === "Escape" &&
        !aboutModal.hidden
    ) {
        closeAboutModal();
    }
});


/* ---------------------------------------------------------
   Add button
   --------------------------------------------------------- */

addButton.addEventListener("click", () => {
    /*
     * Reserved for future ClearPath functionality:
     *
     * - Upload documents
     * - Download forms
     * - Police clearance information
     * - Document checklist
     * - Start eligibility assessment
     */

    messageInput.focus();
});


/* ---------------------------------------------------------
   Initialisation
   --------------------------------------------------------- */

resizeInput();
updateSendButton();      "I want to check whether I may be eligible for expungement or another form of criminal-record relief.",
    assess: true
  },

  record: {
    prompt:
      "I want to understand my criminal record and what possible options I may have.",
    assess: false
  },

  prepare: {
    prompt:
      "I want help preparing for an application for criminal-record relief.",
    assess: false
  }

};


/*
--------------------------------------------------
HEALTH CHECK
--------------------------------------------------
*/

async function checkHealth() {

  try {

    const response =
      await fetch(`${API_BASE}/health`);

    if (!response.ok) {
      throw new Error("Health check failed");
    }

    statusDot.className =
      "status-dot online";

    statusText.textContent =
      "Service online";

  } catch (error) {

    statusDot.className =
      "status-dot offline";

    statusText.textContent =
      "Service unavailable";

    console.error(
      "Health check:",
      error
    );

  }

}


/*
--------------------------------------------------
NEW CHAT
--------------------------------------------------
*/

function startNewChat() {

  messages.innerHTML = "";

  currentPathway = null;

  chatScreen.classList.add("hidden");

  welcomeScreen.classList.remove("hidden");

  messageInput.value = "";

  autoResize();

  messageInput.focus();

}


newChatButton.addEventListener(
  "click",
  startNewChat
);


mobileNewChat.addEventListener(
  "click",
  startNewChat
);


/*
--------------------------------------------------
QUICK ACTIONS
--------------------------------------------------
*/

document
  .querySelectorAll("[data-action]")
  .forEach(button => {

    button.addEventListener(
      "click",
      () => {

        const action =
          button.dataset.action;

        runAction(action);

      }
    );

  });


function runAction(action) {

  const selected =
    ACTIONS[action];

  if (!selected || isSending) {
    return;
  }

  messageInput.value =
    selected.prompt;

  autoResize();

  if (selected.assess) {

    runAssessment(
      selected.prompt
    );

  } else {

    sendMessage(
      selected.prompt
    );

  }

}


/*
--------------------------------------------------
TEXTAREA
--------------------------------------------------
*/

messageInput.addEventListener(
  "input",
  autoResize
);


function autoResize() {

  messageInput.style.height =
    "auto";

  messageInput.style.height =
    Math.min(
      messageInput.scrollHeight,
      180
    ) + "px";

}


messageInput.addEventListener(
  "keydown",
  event => {

    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {

      event.preventDefault();

      chatForm.requestSubmit();

    }

  }
);


/*
--------------------------------------------------
CHAT FORM
--------------------------------------------------
*/

chatForm.addEventListener(
  "submit",
  async event => {

    event.preventDefault();

    const message =
      messageInput.value.trim();

    if (
      !message ||
      isSending
    ) {
      return;
    }

    await sendMessage(message);

  }
);


/*
--------------------------------------------------
ASSESSMENT
--------------------------------------------------
*/

async function runAssessment(message) {

  if (isSending) {
    return;
  }

  isSending = true;

  sendButton.disabled = true;

  showChat();

  addUserMessage(message);

  messageInput.value = "";

  autoResize();

  const typing =
    addTypingIndicator();


  try {

    const response =
      await fetch(
        `${API_BASE}/assess`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json"
          },

          body: JSON.stringify({
            message: message
          })
        }
      );


    const data =
      await parseResponse(
        response
      );


    if (typing) {
      typing.remove();
    }


    addAssessmentMessage(
      data
    );


  } catch (error) {

    if (typing) {
      typing.remove();
    }

    addErrorMessage(
      error,
      message
    );

  } finally {

    isSending = false;

    sendButton.disabled = false;

    messageInput.focus();

  }

}


/*
--------------------------------------------------
CHAT
--------------------------------------------------
*/

async function sendMessage(message) {

  if (
    !message ||
    isSending
  ) {
    return;
  }

  isSending = true;

  sendButton.disabled = true;

  showChat();

  addUserMessage(message);

  messageInput.value = "";

  autoResize();

  const typing =
    addTypingIndicator();


  try {

    const response =
      await fetch(
        `${API_BASE}/chat`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json"
          },

          body: JSON.stringify({
            message: message,
            pathway: currentPathway
          })
        }
      );


    const data =
      await parseResponse(
        response
      );


    if (typing) {
      typing.remove();
    }


    currentPathway =
      data.pathway ||
      currentPathway;


    addAssistantMessage(
      data
    );


  } catch (error) {

    if (typing) {
      typing.remove();
    }

    addErrorMessage(
      error,
      message
    );

    console.error(
      "Chat error:",
      error
    );

  } finally {

    isSending = false;

    sendButton.disabled = false;

    messageInput.focus();

  }

}


/*
--------------------------------------------------
API RESPONSE
--------------------------------------------------
*/

async function parseResponse(
  response
) {

  const data =
    await response
      .json()
      .catch(() => ({}));


  if (!response.ok) {

    throw new Error(
      data?.detail ||
      "The service could not process your request. Please try again."
    );

  }


  return data;

}


/*
--------------------------------------------------
SHOW CHAT
--------------------------------------------------
*/

function showChat() {

  welcomeScreen.classList.add(
    "hidden"
  );

  chatScreen.classList.remove(
    "hidden"
  );

}


/*
--------------------------------------------------
USER MESSAGE
--------------------------------------------------
*/

function addUserMessage(text) {

  const wrapper =
    document.createElement(
      "div"
    );

  wrapper.className =
    "message user";


  const content =
    document.createElement(
      "div"
    );

  content.className =
    "message-content";

  content.textContent =
    text;


  wrapper.appendChild(
    content
  );

  messages.appendChild(
    wrapper
  );

  scrollToBottom();

}


/*
--------------------------------------------------
PATH MESSAGE
--------------------------------------------------
*/

function addAssistantMessage(
  data
) {

  const wrapper =
    document.createElement(
      "div"
    );

  wrapper.className =
    "message assistant";


  const inner =
    document.createElement(
      "div"
    );

  inner.className =
    "message-content";


  inner.appendChild(
    assistantMeta()
  );


  const answer =
    document.createElement(
      "div"
    );

  answer.innerHTML =
    formatResponse(
      data.answer || ""
    );


  inner.appendChild(
    answer
  );


  const info =
    document.createElement(
      "div"
    );

  info.className =
    "response-info";


  if (data.pathway) {

    const pathway =
      document.createElement(
        "span"
      );

    pathway.className =
      "pathway";

    pathway.textContent =
      "Possible pathway: " +
      formatPathway(
        data.pathway
      );

    info.appendChild(
      pathway
    );

  }


  if (
    Array.isArray(
      data.knowledge_sources
    ) &&
    data.knowledge_sources.length
  ) {

    const sources =
      document.createElement(
        "div"
      );

    sources.textContent =
      "Information considered: " +
      data.knowledge_sources.join(
        ", "
      );

    info.appendChild(
      sources
    );

  }


  if (data.next_step) {

    const nextStep =
      document.createElement(
        "div"
      );

    nextStep.className =
      "next-step";

    nextStep.innerHTML =
      "<strong>Possible next step:</strong> " +
      escapeHtml(
        data.next_step
      );

    info.appendChild(
      nextStep
    );

  }


  if (data.uncertainty) {

    const uncertainty =
      document.createElement(
        "div"
      );

    uncertainty.className =
      "uncertainty";

    uncertainty.innerHTML =
      "<strong>Important:</strong> " +
      escapeHtml(
        data.uncertainty
      );

    info.appendChild(
      uncertainty
    );

  }


  if (info.children.length) {

    inner.appendChild(
      info
    );

  }


  wrapper.appendChild(
    inner
  );

  messages.appendChild(
    wrapper
  );

  scrollToBottom();

}


/*
--------------------------------------------------
ASSESSMENT RESULT
--------------------------------------------------
*/

function addAssessmentMessage(
  data
) {

  const wrapper =
    document.createElement(
      "div"
    );

  wrapper.className =
    "message assistant";


  const inner =
    document.createElement(
      "div"
    );

  inner.className =
    "message-content";


  inner.appendChild(
    assistantMeta()
  );


  const intro =
    document.createElement(
      "div"
    );

  intro.textContent =
    data.preliminary_guidance ||
    "This is a preliminary navigation assessment only.";


  inner.appendChild(
    intro
  );


  const card =
    document.createElement(
      "div"
    );

  card.className =
    "assessment-card";


  addAssessmentField(
    card,
    "Possible pathway",
    formatPathway(
      data.possible_pathway
    ) ||
      "Not yet identified."
  );


  addAssessmentField(
    card,
    "What Path needs to know",
    Array.isArray(
      data.information_needed
    ) &&
    data.information_needed.length
      ? data.information_needed.join(
          " "
        )
      : "No additional information was requested by this preliminary assessment."
  );


  addAssessmentField(
    card,
    "Limitations",
    data.disclaimer ||
      "AI assists, not adjudicates."
  );


  inner.appendChild(
    card
  );


  wrapper.appendChild(
    inner
  );

  messages.appendChild(
    wrapper
  );

  scrollToBottom();

}


function addAssessmentField(
  parent,
  title,
  value
) {

  const heading =
    document.createElement(
      "h3"
    );

  heading.textContent =
    title;


  parent.appendChild(
    heading
  );


  const paragraph =
    document.createElement(
      "p"
    );

  paragraph.textContent =
    value;


  parent.appendChild(
    paragraph
  );

}


/*
--------------------------------------------------
PATH IDENTITY
--------------------------------------------------
*/

function assistantMeta() {

  const meta =
    document.createElement(
      "div"
    );

  meta.className =
    "assistant-meta";


  const mark =
    document.createElement(
      "span"
    );

  mark.className =
    "assistant-mark";

  mark.textContent =
    "P";


  const label =
    document.createElement(
      "span"
    );

  label.textContent =
    "Path — Your ClearPath Justice assistant";


  meta.append(
    mark,
    label
  );


  return meta;

}


/*
--------------------------------------------------
ERROR
--------------------------------------------------
*/

function addErrorMessage(
  error,
  retryMessage
) {

  const wrapper =
    document.createElement(
      "div"
    );

  wrapper.className =
    "message assistant";


  const content =
    document.createElement(
      "div"
    );

  content.className =
    "message-content error-message";


  content.innerHTML =
    "<strong>Something went wrong.</strong><br>" +
    escapeHtml(
      error.message ||
      "Please try again in a moment."
    );


  if (retryMessage) {

    const retry =
      document.createElement(
        "button"
      );

    retry.className =
      "retry-button";

    retry.type =
      "button";

    retry.textContent =
      "Try again";


    retry.addEventListener(
      "click",
      () => {

        sendMessage(
          retryMessage
        );

      }
    );


    content.appendChild(
      retry
    );

  }


  wrapper.appendChild(
    content
  );

  messages.appendChild(
    wrapper
  );

  scrollToBottom();

}


/*
--------------------------------------------------
TYPING
--------------------------------------------------
*/

function addTypingIndicator() {

  const wrapper =
    document.createElement(
      "div"
    );

  wrapper.className =
    "message assistant";


  const content =
    document.createElement(
      "div"
    );

  content.className =
    "message-content";


  content.appendChild(
    assistantMeta()
  );


  const typing =
    document.createElement(
      "div"
    );

  typing.className =
    "typing";


  typing.innerHTML =
    `
      <span></span>
      <span></span>
      <span></span>
    `;


  content.appendChild(
    typing
  );


  wrapper.appendChild(
    content
  );

  messages.appendChild(
    wrapper
  );

  scrollToBottom();


  return wrapper;

}


/*
--------------------------------------------------
FORMAT RESPONSE
--------------------------------------------------
*/

function formatResponse(text) {

  let safe =
    escapeHtml(text);


  safe =
    safe.replace(
      /\*\*(.*?)\*\*/g,
      "<strong>$1</strong>"
    );


  safe =
    safe.replace(
      /\n\n/g,
      "<br><br>"
    );


  safe =
    safe.replace(
      /\n/g,
      "<br>"
    );


  return safe;

}


function escapeHtml(text) {

  const div =
    document.createElement(
      "div"
    );

  div.textContent =
    text;

  return div.innerHTML;

}


/*
--------------------------------------------------
PATHWAY
--------------------------------------------------
*/

function formatPathway(
  pathway
) {

  if (!pathway) {
    return "";
  }


  return String(pathway)
    .replace(
      /_/g,
      " "
    )
    .replace(
      /\b\w/g,
      letter =>
        letter.toUpperCase()
    );

}


/*
--------------------------------------------------
SCROLL
--------------------------------------------------
*/

function scrollToBottom() {

  requestAnimationFrame(
    () => {

      chatScreen.scrollTop =
        chatScreen.scrollHeight;

    }
  );

}


/*
--------------------------------------------------
START
--------------------------------------------------
*/

checkHealth();        statusDot.classList.add("online");
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
