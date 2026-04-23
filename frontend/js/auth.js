const SESSION_KEY = "cemaplant.session";

function $(id) {
    return document.getElementById(id);
}

function getBasePath() {
    const path = (window.location.pathname || "").replace(/\\/g, "/");
    return path.includes("/pages/") ? ".." : ".";
}

function irPara(caminhoRelativo) {
    window.location.href = `${getBasePath()}/${caminhoRelativo}`;
}

function salvarSessao(user) {
    localStorage.setItem(SESSION_KEY, JSON.stringify(user));
}

function carregarSessao() {
    try {
        const data = localStorage.getItem(SESSION_KEY);
        return data ? JSON.parse(data) : null;
    } catch (_erro) {
        localStorage.removeItem(SESSION_KEY);
        return null;
    }
}

function limparSessao() {
    localStorage.removeItem(SESSION_KEY);
}

function estaAutenticado() {
    return !!carregarSessao();
}

function exigirAutenticacao() {
    if (!estaAutenticado()) {
        irPara("login.html");
        return false;
    }
    return true;
}

function bloquearParaAutenticado() {
    if (estaAutenticado()) {
        irPara("pages/dashboard.html");
        return true;
    }
    return false;
}

function definirStatus(id, texto, tipo = "") {
    const el = $(id);
    if (!el) {
        return;
    }

    el.textContent = texto;
    if (tipo) {
        el.dataset.state = tipo;
    }
}

async function login() {
    try {
        const nome = $("nomeLogin")?.value.trim();
        const email = $("emailLogin")?.value.trim();
        const senha = $("senhaLogin")?.value;
        if (!nome || !email || !senha) {
            definirStatus("loginStatus", "Preencha nome, email e senha.", "warning");
            return;
        }
        definirStatus("loginStatus", "Autenticando...", "info");
        await apiPost("/usuarios/login", { nome, email, senha });
        salvarSessao({ nome, email });
        definirStatus("loginStatus", "Login realizado com sucesso.", "success");
        irPara("pages/dashboard.html");
    } catch (erro) {
        definirStatus("loginStatus", erro.message || "Falha ao autenticar.", "error");
    }
}

async function registrar() {
    try {
        const nome = $("nomeCadastro")?.value.trim();
        const email = $("emailCadastro")?.value.trim();
        const senha = $("senhaCadastro")?.value;
        if (!nome || !email || !senha) {
            definirStatus("cadastroStatus", "Preencha nome, email e senha.", "warning");
            return;
        }
        definirStatus("cadastroStatus", "Criando conta...", "info");
        await apiPost("/usuarios/registrar", { nome, email, senha });
        definirStatus("cadastroStatus", "Conta criada com sucesso.", "success");
        irPara("login.html");
    } catch (erro) {
        definirStatus("cadastroStatus", erro.message || "Falha ao cadastrar.", "error");
    }
}

function logout() {
    limparSessao();
    irPara("login.html");
}

window.salvarSessao = salvarSessao;
window.carregarSessao = carregarSessao;
window.exigirAutenticacao = exigirAutenticacao;
window.bloquearParaAutenticado = bloquearParaAutenticado;
window.logout = logout;
window.login = login;
window.registrar = registrar;