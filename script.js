"use strict";

/* =========================================================
   DARKIA V2 — FRONTEND ENGINE
   Conectado ao Flask /api/chat
   ========================================================= */

const chatMessages = document.getElementById("chatMessages");
const messageInput = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");
const voiceButton = document.getElementById("voiceButton");
const clearChatButton = document.getElementById("clearChat");

const typingIndicator = document.getElementById("typingIndicator");

const systemStatus = document.getElementById("systemStatus");
const systemHealth = document.getElementById("systemHealth");
const memoryStatus = document.getElementById("memoryStatus");
const knowledgeStatus = document.getElementById("knowledgeStatus");


/* =========================================================
   CONFIGURAÇÃO
   ========================================================= */

const DARKIA_CONFIG = {
    name: "DARKIA",
    version: "2.0",
    apiEndpoint: "/api/chat"
};


/* =========================================================
   HISTÓRICO DA CONVERSA
   ========================================================= */

let conversationHistory = [];


/* =========================================================
   INICIALIZAÇÃO
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    createParticles();

    initializeSystem();

    setupChat();

    setupVoice();

    setupTextarea();

    checkServer();

});


/* =========================================================
   SISTEMA
   ========================================================= */

function initializeSystem() {

    systemStatus.textContent = "ONLINE";
    systemHealth.textContent = "ESTÁVEL";
    memoryStatus.textContent = "ATIVA";
    knowledgeStatus.textContent = "DISPONÍVEL";

}


/* =========================================================
   VERIFICAR SERVIDOR
   ========================================================= */

async function checkServer() {

    try {

        const response = await fetch("/api/status");

        if (!response.ok) {
            throw new Error("Servidor offline");
        }

        const data = await response.json();

        systemStatus.textContent =
            String(data.status || "ONLINE").toUpperCase();

        systemHealth.textContent = "ESTÁVEL";

    } catch (error) {

        console.warn("Servidor DARKIA indisponível.");

        systemStatus.textContent = "OFFLINE";
        systemHealth.textContent = "AGUARDANDO";

    }

}


/* =========================================================
   PARTÍCULAS
   ========================================================= */

function createParticles() {

    const container =
        document.getElementById("particles");

    if (!container) return;

    for (let i = 0; i < 35; i++) {

        const particle =
            document.createElement("span");

        particle.className = "particle";

        particle.style.left =
            Math.random() * 100 + "%";

        particle.style.animationDuration =
            (7 + Math.random() * 14) + "s";

        particle.style.animationDelay =
            (-Math.random() * 15) + "s";

        particle.style.opacity =
            0.2 + Math.random() * 0.8;

        container.appendChild(particle);

    }

}


/* =========================================================
   CHAT
   ========================================================= */

function setupChat() {

    sendButton.addEventListener(
        "click",
        sendMessage
    );

    clearChatButton.addEventListener(
        "click",
        clearChat
    );

    messageInput.addEventListener(
        "keydown",
        event => {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                sendMessage();

            }

        }
    );

}


/* =========================================================
   ENVIAR MENSAGEM
   ========================================================= */

async function sendMessage() {

    const message =
        messageInput.value.trim();

    if (!message) return;


    addUserMessage(message);

    conversationHistory.push({
        role: "user",
        content: message
    });


    messageInput.value = "";

    resetTextareaHeight();

    showTyping();


    try {

        const response =
            await fetch(
                DARKIA_CONFIG.apiEndpoint,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        message: message,
                        history: conversationHistory
                    })
                }
            );


        if (!response.ok) {

            throw new Error(
                `HTTP ${response.status}`
            );

        }


        const data =
            await response.json();


        const answer =
            data.response ||
            "A DARKIA não retornou uma resposta.";


        hideTyping();

        addDarkiaMessage(answer);


        conversationHistory.push({
            role: "assistant",
            content: answer
        });


    } catch (error) {

        console.error(
            "Erro de comunicação:",
            error
        );

        hideTyping();

        addDarkiaMessage(
            "⚠️ Não consegui comunicar com o núcleo da DARKIA. Verifica se o servidor Flask está em execução."
        );

        systemStatus.textContent = "ERRO";

    }

}


/* =========================================================
   MENSAGEM DO UTILIZADOR
   ========================================================= */

function addUserMessage(message) {

    const element =
        document.createElement("div");

    element.className =
        "message user-message";


    const avatar =
        document.createElement("div");

    avatar.className =
        "message-avatar";

    avatar.textContent = "👤";


    const content =
        document.createElement("div");

    content.className =
        "message-content";


    const name =
        document.createElement("div");

    name.className =
        "message-name";

    name.textContent =
        "UTILIZADOR";


    const text =
        document.createElement("div");

    text.className =
        "message-text";

    text.textContent = message;


    content.appendChild(name);
    content.appendChild(text);

    element.appendChild(avatar);
    element.appendChild(content);

    chatMessages.appendChild(element);

    scrollChatToBottom();

}


/* =========================================================
   MENSAGEM DA DARKIA
   ========================================================= */

function addDarkiaMessage(message) {

    const element =
        document.createElement("div");

    element.className =
        "message darkia-message";


    const avatar =
        document.createElement("div");

    avatar.className =
        "message-avatar";

    avatar.textContent = "◈";


    const content =
        document.createElement("div");

    content.className =
        "message-content";


    const name =
        document.createElement("div");

    name.className =
        "message-name";

    name.textContent =
        "DARKIA";


    const text =
        document.createElement("div");

    text.className =
        "message-text";

    text.textContent = message;


    content.appendChild(name);
    content.appendChild(text);

    element.appendChild(avatar);
    element.appendChild(content);

    chatMessages.appendChild(element);

    scrollChatToBottom();

}


/* =========================================================
   PROCESSAMENTO
   ========================================================= */

function showTyping() {

    typingIndicator.hidden = false;

    sendButton.disabled = true;

    scrollChatToBottom();

}


function hideTyping() {

    typingIndicator.hidden = true;

    sendButton.disabled = false;

}


/* =========================================================
   SCROLL
   ========================================================= */

function scrollChatToBottom() {

    requestAnimationFrame(() => {

        chatMessages.scrollTop =
            chatMessages.scrollHeight;

    });

}


/* =========================================================
   LIMPAR CONVERSA
   ========================================================= */

function clearChat() {

    conversationHistory = [];

    chatMessages.innerHTML = "";

    addDarkiaMessage(
        "Conversa reiniciada. O núcleo da DARKIA continua online. 🧠"
    );

}


/* =========================================================
   TEXTAREA
   ========================================================= */

function setupTextarea() {

    messageInput.addEventListener(
        "input",
        resizeTextarea
    );

}


function resizeTextarea() {

    messageInput.style.height =
        "auto";

    messageInput.style.height =
        Math.min(
            messageInput.scrollHeight,
            120
        ) + "px";

}


function resetTextareaHeight() {

    messageInput.style.height =
        "42px";

}


/* =========================================================
   VOZ
   ========================================================= */

function setupVoice() {

    if (!voiceButton) return;


    const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;


    if (!SpeechRecognition) {

        voiceButton.title =
            "Reconhecimento de voz não disponível.";

        return;

    }


    const recognition =
        new SpeechRecognition();


    recognition.lang = "pt-PT";

    recognition.continuous = false;

    recognition.interimResults = false;


    voiceButton.addEventListener(
        "click",
        () => {

            try {

                recognition.start();

                voiceButton.textContent = "🔴";

            } catch (error) {

                console.log(error);

            }

        }
    );


    recognition.onresult =
        event => {

            const transcript =
                event.results[0][0].transcript;

            messageInput.value =
                transcript;

            resizeTextarea();

        };


    recognition.onend =
        () => {

            voiceButton.textContent =
                "🎙️";

        };


    recognition.onerror =
        error => {

            console.warn(
                "Erro de voz:",
                error
            );

            voiceButton.textContent =
                "🎙️";

        };

}


/* =========================================================
   API PÚBLICA
   ========================================================= */

window.DARKIA = {

    sendMessage,

    addDarkiaMessage,

    addUserMessage,

    clearChat,

    checkServer,

    setStatus(status) {

        systemStatus.textContent =
            String(status).toUpperCase();

    },

    setHealth(status) {

        systemHealth.textContent =
            String(status).toUpperCase();

    },

    setMemory(status) {

        memoryStatus.textContent =
            String(status).toUpperCase();

    }

};
