"use strict";


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
   ========================================================== /* =========================================================
   HISTÓRICO DA CONVERSA
   ========================================================= *//* =========================================================
   HISTÓRICO DA CONVERSA
   ========================================================= */

let conversationHistory = [];
let currentConversationId = null;


/* =========================================================
   INICIALIZAÇÃO
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    createParticles();

    initializeSystem();

    setupChat();

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
                        history: conversationHistory,
                        conversation_id: currentConversationId
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

        if (data.conversation_id) {
            currentConversationId = data.conversation_id;
        }


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

/* =========================================================
   DARKIA — VOICE CHAT
   ========================================================= */

(function () {
    function iniciarDarkiaCall() {
        const voiceButton = document.getElementById("voiceButton");
        const darkiaCall = document.getElementById("darkiaCall");
        const micButton = document.getElementById("darkiaMicButton");
        const endButton = document.getElementById("darkiaEndCall");
        const status = document.getElementById("darkiaVoiceStatus");

        if (!voiceButton || !darkiaCall || !micButton || !endButton) {
            console.error("DARKIA CALL: elementos não encontrados.");
            return;
        }

        const SpeechRecognition =
            window.SpeechRecognition ||
            window.webkitSpeechRecognition;

        let recognition = null;
        let ouvindo = false;

        function abrirCall() {
            darkiaCall.hidden = false;
            document.body.style.overflow = "hidden";
            status.textContent = "PRONTA PARA OUVIR";
        }

        function fecharCall() {
            if (recognition && ouvindo) {
                recognition.stop();
            }

            ouvindo = false;
            darkiaCall.classList.remove("call-listening");
            darkiaCall.classList.remove("call-speaking");

            darkiaCall.hidden = true;
            document.body.style.overflow = "";
            status.textContent = "PRONTA PARA OUVIR";
        }

        function falar(texto) {
            if (!("speechSynthesis" in window)) return;

            speechSynthesis.cancel();

            const fala = new SpeechSynthesisUtterance(texto);

            // Mantém a voz padrão/original do dispositivo.
            fala.lang = "pt-PT";

            darkiaCall.classList.remove("call-listening");
            darkiaCall.classList.add("call-speaking");
            status.textContent = "DARKIA A FALAR...";

            fala.onend = function () {
                darkiaCall.classList.remove("call-speaking");
                status.textContent = "PRONTA PARA OUVIR";
            };

            speechSynthesis.speak(fala);
        }

        async function enviarParaDarkia(texto) {
            status.textContent = "DARKIA A PROCESSAR...";

            try {
                const resposta = await fetch("/api/chat", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        message: texto,
                        history: []
                    })
                });

                const data = await resposta.json();
                const respostaDarkia =
                    data.response || "Não consegui responder agora.";

                falar(respostaDarkia);

            } catch (erro) {
                console.error("DARKIA CALL:", erro);
                status.textContent = "ERRO DE CONEXÃO";
            }
        }

        function ouvir() {
            if (!SpeechRecognition) {
                status.textContent = "VOZ NÃO SUPORTADA";
                return;
            }

            if (ouvindo) return;

            recognition = new SpeechRecognition();

            recognition.lang = "pt-PT";
            recognition.continuous = false;
            recognition.interimResults = false;

            recognition.onstart = function () {
                ouvindo = true;
                darkiaCall.classList.add("call-listening");
                status.textContent = "A OUVIR...";
            };

            recognition.onresult = function (event) {
                const texto = event.results[0][0].transcript;

                ouvindo = false;
                darkiaCall.classList.remove("call-listening");

                if (texto.trim()) {
                    enviarParaDarkia(texto.trim());
                }
            };

            recognition.onerror = function (event) {
                console.error("Reconhecimento de voz:", event.error);
                ouvindo = false;
                darkiaCall.classList.remove("call-listening");
                status.textContent = "PRONTA PARA OUVIR";
            };

            recognition.onend = function () {
                ouvindo = false;
                darkiaCall.classList.remove("call-listening");
            };

            recognition.start();
        }

        voiceButton.addEventListener("click", function (event) {
            event.preventDefault();
            event.stopPropagation();
            abrirCall();
        });

        micButton.addEventListener("click", function (event) {
            event.preventDefault();
            event.stopPropagation();
            ouvir();
        });

        endButton.addEventListener("click", function (event) {
            event.preventDefault();
            event.stopPropagation();
            fecharCall();
        });

        console.log("DARKIA CALL: ativado."); alert("DARKIA CALL: JavaScript ativado!");
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", iniciarDarkiaCall);
    } else {
        iniciarDarkiaCall();
    }
})();


/* DARKIA VOICE CLICK TEST */
document.addEventListener("DOMContentLoaded", function () {
    const botao = document.getElementById("voiceButton");
    const janela = document.getElementById("darkiaCall");

    if (!botao || !janela) {
        console.error("VOICE TEST: elementos não encontrados.");
        return;
    }

    botao.onclick = function () {
        console.log("VOICE TEST: clique recebido");
        janela.hidden = false;
        janela.removeAttribute("hidden");
        document.body.style.overflow = "hidden";
        console.log("VOICE TEST: janela aberta");
    };

    console.log("VOICE TEST: listener instalado");
});


/* =========================================================
   DARKIA — MENU LATERAL
   ========================================================= */

(function () {

    function iniciarMenu() {

        const menuButton =
            document.getElementById("menuButton");

        const sideMenu =
            document.getElementById("sideMenu");

        const closeMenu =
            document.getElementById("closeMenu");

        const menuOverlay =
            document.getElementById("menuOverlay");

        const menuNewChat =
            document.getElementById("menuNewChat");

        const menuVoice =
            document.getElementById("menuVoice");

        const menuStatus =
            document.getElementById("menuStatus");

        const menuAbout =
            document.getElementById("menuAbout");

        if (
            !menuButton ||
            !sideMenu ||
            !closeMenu ||
            !menuOverlay
        ) {
            console.error(
                "DARKIA MENU: elementos não encontrados."
            );

            return;
        }


        function abrirMenu() {

            sideMenu.classList.add("active");
            menuOverlay.classList.add("active");
            menuButton.classList.add("active");

            menuButton.setAttribute(
                "aria-expanded",
                "true"
            );

            sideMenu.setAttribute(
                "aria-hidden",
                "false"
            );
        }


        function fecharMenu() {

            sideMenu.classList.remove("active");
            menuOverlay.classList.remove("active");
            menuButton.classList.remove("active");

            menuButton.setAttribute(
                "aria-expanded",
                "false"
            );

            sideMenu.setAttribute(
                "aria-hidden",
                "true"
            );
        }


        function alternarMenu() {

            if (sideMenu.classList.contains("active")) {
                fecharMenu();
            } else {
                abrirMenu();
            }

        }


        menuButton.addEventListener(
            "click",
            alternarMenu
        );

        closeMenu.addEventListener(
            "click",
            fecharMenu
        );

        menuOverlay.addEventListener(
            "click",
            fecharMenu
        );


        /* ESC fecha o menu */

        document.addEventListener(
            "keydown",
            function (event) {

                if (
                    event.key === "Escape" &&
                    sideMenu.classList.contains("active")
                ) {
                    fecharMenu();
                }

            }
        );


        /* NOVA CONVERSA */

        if (menuNewChat) {

            menuNewChat.addEventListener(
                "click",
                function () {

                    fecharMenu();

                    if (
                        typeof clearChat ===
                        "function"
                    ) {
                        clearChat();
                    }

                    if (messageInput) {
                        messageInput.focus();
                    }

                }
            );

        }


        /* VOICE CHAT */

        if (menuVoice) {

            menuVoice.addEventListener(
                "click",
                function () {

                    fecharMenu();

                    const voiceButton =
                        document.getElementById(
                            "voiceButton"
                        );

                    if (voiceButton) {
                        voiceButton.click();
                    }

                }
            );

        }


        /* STATUS */

        if (menuStatus) {

            menuStatus.addEventListener(
                "click",
                function () {

                    fecharMenu();

                    const statusAtual =
                        systemStatus
                            ? systemStatus.textContent
                            : "DESCONHECIDO";

                    if (
                        typeof addDarkiaMessage ===
                        "function"
                    ) {

                        addDarkiaMessage(
                            "Status do sistema: " +
                            statusAtual +
                            ". Núcleo da DARKIA operacional."
                        );

                    }

                }
            );

        }


        /* SOBRE */

        if (menuAbout) {

            menuAbout.addEventListener(
                "click",
                function () {

                    fecharMenu();

                    if (
                        typeof addDarkiaMessage ===
                        "function"
                    ) {

                        addDarkiaMessage(
                            "DARKIA AI CORE V2.0 — Inteligência Artificial desenvolvida por BG (Basilua) e Ibram (Marbi)."
                        );

                    }

                }
            );

        }


        console.log(
            "DARKIA MENU: ativado."
        );

    }


    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            iniciarMenu
        );

    } else {

        iniciarMenu();

    }

})();

/* =========================================================
   DARKIA — AUTENTICAÇÃO
   ========================================================= */

(function setupAuthentication() {
    const authScreen = document.getElementById("authScreen");
    const authForm = document.getElementById("authForm");
    const authUsername = document.getElementById("authUsername");
    const authPassword = document.getElementById("authPassword");
    const authSubmit = document.getElementById("authSubmit");
    const authMessage = document.getElementById("authMessage");

    const loginTab = document.getElementById("loginTab");
    const registerTab = document.getElementById("registerTab");

    if (!authScreen || !authForm) {
        console.warn("DARKIA AUTH: elementos não encontrados.");
        return;
    }

    let registerMode = false;

    function showMessage(message, error = true) {
        authMessage.textContent = message;
        authMessage.style.color = error ? "#ff6688" : "#00ff9d";
    }

    function setMode(register) {
        registerMode = register;

        loginTab.classList.toggle("active", !register);
        registerTab.classList.toggle("active", register);

        authSubmit.textContent = register
            ? "CRIAR CONTA"
            : "ENTRAR NA DARKIA";

        authPassword.autocomplete = register
            ? "new-password"
            : "current-password";

        authPassword.value = "";
        showMessage("");
    }

    loginTab.addEventListener("click", () => {
        setMode(false);
    });

    registerTab.addEventListener("click", () => {
        setMode(true);
    });

    authForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const username = authUsername.value.trim();
        const password = authPassword.value;

        if (!username || !password) {
            showMessage("Preenche todos os campos.");
            return;
        }

        authSubmit.disabled = true;
        authSubmit.textContent = registerMode
            ? "A CRIAR..."
            : "A ENTRAR...";

        try {
            const endpoint = registerMode
                ? "/api/register"
                : "/api/login";

            const response = await fetch(endpoint, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    username,
                    password
                })
            });

            const data = await response.json();

            if (!response.ok) {
                showMessage(
                    data.response || "Não foi possível concluir a operação."
                );

                authSubmit.disabled = false;
                authSubmit.textContent = registerMode
                    ? "CRIAR CONTA"
                    : "ENTRAR NA DARKIA";

                return;
            }

            showMessage(
                `Bem-vindo, ${data.user.username}!`,
                false
            );

            setTimeout(() => {
                authScreen.style.display = "none";
                document.body.classList.remove("auth-locked");

                console.log(
                    "DARKIA AUTH: sessão iniciada como",
                    data.user.username
                );
            }, 500);

        } catch (error) {
            console.error("DARKIA AUTH:", error);

            showMessage(
                "Não foi possível contactar a DARKIA."
            );

            authSubmit.disabled = false;
            authSubmit.textContent = registerMode
                ? "CRIAR CONTA"
                : "ENTRAR NA DARKIA";
        }
    });


    async function checkSession() {
        try {
            const response = await fetch("/api/me");
            const data = await response.json();

            if (data.logged_in) {
                authScreen.style.display = "none";
                document.body.classList.remove("auth-locked");

                console.log(
                    "DARKIA AUTH: sessão recuperada.",
                    data.user.username
                );
            } else {
                authScreen.style.display = "flex";
                document.body.classList.add("auth-locked");
            }

        } catch (error) {
            console.error(
                "DARKIA AUTH: erro ao verificar sessão.",
                error
            );
        }
    }

    document.body.classList.add("auth-locked");

    checkSession();

})();

/* =========================================================
   DARKIA — HISTÓRICO E CONTA
   ========================================================= */

(function setupHistoryAndAccount() {

    const menuHistory = document.getElementById("menuHistory");
    const menuAccount = document.getElementById("menuAccount");
    const menuLogout = document.getElementById("menuLogout");

    if (!menuHistory) return;

    function criarPainel(id, titulo, conteudo) {
        let painel = document.getElementById(id);

        if (!painel) {
            painel = document.createElement("div");
            painel.id = id;
            painel.className = "history-panel";

            painel.innerHTML = `
                <div class="history-card">
                    <div class="history-header">
                        <h2>${titulo}</h2>
                        <button class="history-close" type="button">✕</button>
                    </div>
                    <div class="history-content">
                        ${conteudo}
                    </div>
                </div>
            `;

            document.body.appendChild(painel);

            painel.querySelector(".history-close")
                .addEventListener("click", () => {
                    painel.classList.remove("active");
                });

            painel.addEventListener("click", (event) => {
                if (event.target === painel) {
                    painel.classList.remove("active");
                }
            });
        }

        return painel;
    }


    async function abrirHistorico() {

        const painel = criarPainel(
            "historyPanel",
            "HISTÓRICO",
            `<div class="history-list" id="historyList">
                <div class="history-empty">A carregar...</div>
            </div>`
        );

        painel.classList.add("active");

        const lista = document.getElementById("historyList");

        try {

            const response = await fetch("/api/conversations");
            const data = await response.json();

            if (!response.ok) {
                lista.innerHTML =
                    `<div class="history-empty">
                        ${data.response || "Erro ao carregar histórico."}
                    </div>`;
                return;
            }

            if (!data.conversations.length) {
                lista.innerHTML =
                    `<div class="history-empty">
                        Ainda não tens conversas guardadas.
                    </div>`;
                return;
            }

            lista.innerHTML = "";

            data.conversations.forEach(conversation => {

                const item = document.createElement("button");

                item.className = "history-item";

                item.innerHTML = `
                    <strong>💬 ${conversation.title}</strong>
                    <small>${conversation.updated_at}</small>
                `;

                item.addEventListener("click", async () => {

                    try {

                        const result = await fetch(
                            `/api/conversations/${conversation.id}`
                        );

                        const data = await result.json();

                        if (!result.ok) return;

                        currentConversationId = conversation.id;

                        const chatMessages =
                            document.getElementById("chatMessages");

                        if (chatMessages) {
                            chatMessages.innerHTML = "";

                            conversationHistory = [];

                            data.messages.forEach(message => {

                                conversationHistory.push({
                                    role: message.role,
                                    content: message.content
                                });

                                const div =
                                    document.createElement("div");

                                div.className =
                                    message.role === "user"
                                        ? "message user-message"
                                        : "message ai-message";

                                div.textContent = message.content;

                                chatMessages.appendChild(div);
                            });
                        }

                        painel.classList.remove("active");

                    } catch (error) {
                        console.error(
                            "DARKIA HISTORY:",
                            error
                        );
                    }
                });

                lista.appendChild(item);
            });

        } catch (error) {

            console.error(
                "DARKIA HISTORY:",
                error
            );

            lista.innerHTML =
                `<div class="history-empty">
                    Não foi possível carregar o histórico.
                </div>`;
        }
    }


    async function abrirConta() {

        try {

            const response = await fetch("/api/me");
            const data = await response.json();

            if (!data.logged_in) return;

            const painel = criarPainel(
                "accountPanel",
                "MINHA CONTA",
                `
                <div class="account-info">
                    <div class="account-avatar">👤</div>

                    <strong>${data.user.username}</strong>

                    <small>
                        Conta DARKIA
                    </small>
                </div>
                `
            );

            painel.classList.add("active");

        } catch (error) {

            console.error(
                "DARKIA ACCOUNT:",
                error
            );
        }
    }


    menuHistory.addEventListener("click", () => {
        abrirHistorico();
    });


    menuAccount.addEventListener("click", () => {
        abrirConta();
    });


    if (menuLogout) {

        menuLogout.addEventListener("click", async () => {

            const response = await fetch(
                "/api/logout",
                {
                    method: "POST"
                }
            );

            const data = await response.json();

            if (response.ok) {

                const authScreen =
                    document.getElementById("authScreen");

                if (authScreen) {
                    authScreen.style.display = "flex";
                }

                document.body.classList.add("auth-locked");

                const username =
                    document.getElementById("authUsername");

                const password =
                    document.getElementById("authPassword");

                if (username) username.value = "";
                if (password) password.value = "";

                console.log(
                    "DARKIA AUTH: sessão terminada."
                );
            }

        });
    }

})();


