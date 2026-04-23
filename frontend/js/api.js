const API_URL = "http://localhost:8000";

function normalizarErro(payload, response) {
    if (!payload) {
        return `Erro HTTP ${response.status}`;
    }
    if (typeof payload.detail === "string") {
        return payload.detail;
    }
    if (Array.isArray(payload.detail) && payload.detail.length > 0) {
        return payload.detail
            .map((item) => item.msg || item.message || JSON.stringify(item))
            .join("; ");
    }
    if (typeof payload.message === "string") {
        return payload.message;
    }
    return `Erro HTTP ${response.status}`;
}

async function requisicaoJson(url, options = {}) {
    const { headers = {}, body, ...rest } = options;
    const config = {
        credentials: "include",
        ...rest,
        headers: {
            Accept: "application/json",
            ...headers
        }
    };
    if (body instanceof FormData) {
        config.body = body;
    } else if (body !== undefined) {
        config.body = typeof body === "string" ? body : JSON.stringify(body);
        config.headers = {
            "Content-Type": "application/json",
            ...config.headers
        };
    }
    const response = await fetch(`${API_URL}${url}`, config);
    const contentType = response.headers.get("content-type") || "";
    let payload = null;
    if (contentType.includes("application/json")) {
        payload = await response.json();
    } else {
        const texto = await response.text();
        payload = texto ? { detail: texto } : null;
    }
    if (!response.ok) {
        const erro = new Error(normalizarErro(payload, response));
        erro.status = response.status;
        erro.payload = payload;
        throw erro;
    }
    return payload;
}

function apiGet(url) {
    return requisicaoJson(url, { method: "GET" });
}

function apiPost(url, body) {
    return requisicaoJson(url, { method: "POST", body });
}

function resolverUrlImagem(caminho) {
    if (!caminho || typeof caminho !== "string") {
        console.warn("[API] URL vazia ou inválida");
        return "";
    }
    const normalizado = caminho.replace(/\\\\/g, "/").replace(/\\/g, "/").trim();
    console.log(`[API] Resolvendo: '${caminho}' → '${normalizado}'`);
    if (/^https?:\/\//i.test(normalizado)) {
        console.log(`[API] → Já é URL absoluta`);
        return normalizado;
    }
    if (normalizado.startsWith("/uploads/")) {
        const resultado = `${API_URL}${normalizado}`;
        console.log(`[API] → Começa com /uploads: ${resultado}`);
        return resultado;
    }
    const markerAppUploads = "app/uploads/";
    const idxApp = normalizado.indexOf(markerAppUploads);
    if (idxApp >= 0) {
        const relativo = normalizado.slice(idxApp + markerAppUploads.length);
        const resultado = `${API_URL}/uploads/${relativo}`;
        console.log(`[API] → Contém ${markerAppUploads}: ${resultado}`);
        return resultado;
    }
    if (!normalizado.startsWith("/") && !normalizado.includes("://")) {
        const resultado = `${API_URL}/uploads/${normalizado}`;
        console.log(`[API] → Caminho relativo, assumindo /uploads: ${resultado}`);
        return resultado;
    }
    console.log(`[API] → Retornando como está: ${normalizado}`);
    return normalizado;
}

window.addEventListener("DOMContentLoaded", () => {
    console.log("App iniciado");
});

window.requisicaoJson = requisicaoJson;
window.apiGet = apiGet;
window.apiPost = apiPost;
window.resolverUrlImagem = resolverUrlImagem;