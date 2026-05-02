function $(id) {
    return document.getElementById(id);
}

const TIMEZONE_BRASILIA = "America/Sao_Paulo";

function parseDataBackend(valor) {
    if (valor instanceof Date) {
        return valor;
    }
    if (typeof valor === "string") {
        const texto = valor.trim();
        const temFuso = /([zZ]|[+-]\d{2}:?\d{2})$/.test(texto);
        if (temFuso) {
            return new Date(texto.replace(" ", "T"));
        }
        const m = texto.match(
            /^(\d{4})-(\d{2})-(\d{2})(?:[ T](\d{2}):(\d{2})(?::(\d{2})(?:\.(\d{1,6}))?)?)?$/
        );
        if (m) {
            const ano = Number(m[1]);
            const mes = Number(m[2]) - 1;
            const dia = Number(m[3]);
            const hora = Number(m[4] || 0);
            const minuto = Number(m[5] || 0);
            const segundo = Number(m[6] || 0);
            const micros = m[7] || "0";
            const ms = Number(micros.slice(0, 3).padEnd(3, "0"));
            return new Date(Date.UTC(ano, mes, dia, hora, minuto, segundo, ms));
        }
        return new Date(`${texto.replace(" ", "T")}Z`);
    }
    return new Date(valor);
}

function formatarData(valor) {
    if (!valor) {
        return "-";
    }

    const data = parseDataBackend(valor);
    if (Number.isNaN(data.getTime())) {
        return valor;
    }

    return new Intl.DateTimeFormat("pt-BR", {
        dateStyle: "short",
        timeStyle: "short",
        timeZone: TIMEZONE_BRASILIA
    }).format(data);
}

function formatarPercentual(valor) {
    const numero = Number(valor);
    return Number.isNaN(numero) ? "-" : `${(numero * 100).toFixed(2)}%`;
}

function definirStatus(texto, tipo = "") {
    const el = $("uploadStatus");
    if (!el) {
        return;
    }

    el.textContent = texto;
    if (tipo) {
        el.dataset.state = tipo;
    }
}

function arquivoEhJpgOuPng(file) {
    if (!file) {
        return false;
    }

    const mime = (file.type || "").toLowerCase();
    const nome = (file.name || "").toLowerCase();

    if (mime === "image/jpeg" || mime === "image/png") {
        return true;
    }

    return /\.(jpg|jpeg|png)$/i.test(nome);
}

function atualizarPreview() {
    const input = $("imagem");
    const preview = $("previewImagem");
    const fallback = $("imagemNome");

    if (!input || !preview || !fallback) {
        return;
    }

    const file = input.files?.[0];
    if (!file) {
        preview.hidden = true;
        preview.src = "";
        fallback.textContent = "Nenhum arquivo selecionado";
        return;
    }

    if (!arquivoEhJpgOuPng(file)) {
        preview.hidden = true;
        preview.src = "";
        input.value = "";
        fallback.textContent = "Formato inválido";
        definirStatus("Envie apenas imagens JPG ou PNG.", "warning");
        return;
    }

    fallback.textContent = file.name;
    const url = URL.createObjectURL(file);
    preview.src = url;
    preview.hidden = false;
    preview.onload = () => URL.revokeObjectURL(url);
}

function renderizarResultado(data) {
    const el = $("resultado");
    if (!el) {
        return;
    }
    el.innerHTML = "";
    const card = document.createElement("div");
    card.className = "result-card";

    const titulo = document.createElement("h3");
    titulo.textContent = `Detecção #${data.id}`;
    card.appendChild(titulo);

    const grid = document.createElement("div");
    grid.className = "result-grid";

    const campos = [
        ["Confiança", formatarPercentual(data.porcentagem_confianca)],
        ["Data", formatarData(data.data_deteccao)],
        ["Imagem ID", String(data.imagem_id)],
        ["Planta ID", String(data.planta_id)],
        ["classe ID", String(data.doenca_id)]
    ];

    campos.forEach(([label, value]) => {
        const bloco = document.createElement("div");
        bloco.className = "result-metric";
        const l = document.createElement("span");
        l.textContent = label;
        const v = document.createElement("strong");
        v.textContent = value;
        bloco.appendChild(l);
        bloco.appendChild(v);
        grid.appendChild(bloco);
    });
    card.appendChild(grid);
    const rec = document.createElement("p");
    rec.className = "result-text";
    rec.textContent = data.recomendacao || "Sem recomendação disponível.";
    card.appendChild(rec);
    el.appendChild(card);
}

async function enviarImagem() {
    if (!exigirAutenticacao()) {
        return;
    }
    try {
        const file = $("imagem")?.files?.[0];
        if (!file) {
            definirStatus("Selecione uma imagem para enviar.", "warning");
            return;
        }
        if (!arquivoEhJpgOuPng(file)) {
            definirStatus("Formato inválido. Use JPG ou PNG.", "warning");
            return;
        }
        definirStatus("Enviando imagem para análise...", "info");
        const formData = new FormData();
        formData.append("file", file);
        const data = await requisicaoJson("/deteccoes/", {
            method: "POST",
            body: formData
        });
        renderizarResultado(data);
        definirStatus("Detecção concluída com sucesso.", "success");
    } catch (erro) {
        definirStatus(erro.message || "Falha ao processar imagem.", "error");
    }
}

window.enviarImagem = enviarImagem;

window.addEventListener("DOMContentLoaded", () => {
    const root = $("uploadPage");
    if (!root) {
        return;
    }
    if (!exigirAutenticacao()) {
        return;
    }
    const input = $("imagem");
    if (input) {
        input.addEventListener("change", atualizarPreview);
    }
});