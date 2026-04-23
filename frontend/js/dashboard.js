function $(id) {
    return document.getElementById(id);
}

function setText(id, value) {
    const el = $(id);
    if (el) {
        el.textContent = String(value);
    }
}

function setStatus(texto, tipo = "") {
    const el = $("dashboardStatus");
    if (!el) {
        return;
    }
    el.textContent = texto;
    if (tipo) {
        el.dataset.state = tipo;
    }
}

function formatarData(valor) {
    if (!valor) {
        return "-";
    }
    const data = new Date(valor);
    if (Number.isNaN(data.getTime())) {
        return valor;
    }
    return new Intl.DateTimeFormat("pt-BR", {
        dateStyle: "short",
        timeStyle: "short"
    }).format(data);
}

function formatarPercentual(valor) {
    const n = Number(valor);
    if (Number.isNaN(n)) {
        return "-";
    }
    return `${(n * 100).toFixed(2)}%`;
}

function imagemEhJpgOuPng(caminho) {
    if (!caminho || typeof caminho !== "string") {
        return false;
    }

    const semQuery = caminho.split("?")[0].toLowerCase();
    return /\.(jpg|jpeg|png)$/i.test(semQuery);
}

function formatarNomeDoenca(nome) {
    if (!nome || typeof nome !== "string") {
        return "-";
    }

    const parteDoenca = nome.includes("___") ? nome.split("___")[1] : nome;
    return parteDoenca.replace(/_/g, " ").trim();
}

function renderizarGaleria(imagens, deteccoes, plantas, doencas) {
    const galeria = $("deteccoesGaleria");
    if (!galeria) {
        return;
    }
    galeria.innerHTML = "";
    if (!Array.isArray(imagens) || imagens.length === 0) {
        const vazio = document.createElement("div");
        vazio.className = "empty-state";
        vazio.textContent = "Nenhuma imagem detectada ainda.";
        galeria.appendChild(vazio);
        return;
    }
    const imagensValidas = imagens.filter((img) => imagemEhJpgOuPng(img?.url_imagem));
    if (imagensValidas.length === 0) {
        const vazio = document.createElement("div");
        vazio.className = "empty-state";
        vazio.textContent = "Não há imagens JPG/PNG para exibir.";
        galeria.appendChild(vazio);
        return;
    }
    const mapaDeteccaoPorImagem = new Map();
    if (Array.isArray(deteccoes)) {
        deteccoes.forEach((d) => {
            if (d && d.imagem_id !== undefined) {
                mapaDeteccaoPorImagem.set(d.imagem_id, d);
            }
        });
    }
    const mapaPlantasPorId = new Map();
    if (Array.isArray(plantas)) {
        plantas.forEach((p) => {
            if (p && p.id !== undefined) {
                mapaPlantasPorId.set(p.id, p);
            }
        });
    }

    const mapaDoencasPorId = new Map();
    if (Array.isArray(doencas)) {
        doencas.forEach((d) => {
            if (d && d.id !== undefined) {
                mapaDoencasPorId.set(d.id, d);
            }
        });
    }
    imagensValidas.slice(0, 12).forEach((img) => {
        const card = document.createElement("article");
        card.className = "thumb-card";
        const preview = document.createElement("img");
        preview.className = "thumb-card__image";
        preview.alt = `Imagem detectada ${img.id}`;
        preview.loading = "lazy";
        const urlResolvida = resolverUrlImagem(img.url_imagem);
        console.log(`[GALERIA] Carregando imagem ${img.id}: ${img.url_imagem} → ${urlResolvida}`);
        preview.src = urlResolvida;
        preview.onerror = () => {
            console.error(`[GALERIA] Erro ao carregar imagem ${img.id} de ${urlResolvida}`);
            preview.style.backgroundColor = "rgba(35, 69, 93, 0.1)";
            // Usar um placeholder SVG como fallback
            preview.src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Crect fill='%23f0f0f0' width='200' height='200'/%3E%3Ctext x='100' y='100' font-family='Arial' font-size='20' fill='%23999' text-anchor='middle' dy='.3em'%3E❌ Erro%3C/text%3E%3C/svg%3E";
        };
        preview.onload = () => {
            console.log(`[GALERIA] Imagem ${img.id} carregada com sucesso`);
        };
        const body = document.createElement("div");
        body.className = "thumb-card__body";
        const titulo = document.createElement("strong");
        const det = mapaDeteccaoPorImagem.get(img.id);
        const nomePlanta = det ? mapaPlantasPorId.get(det.planta_id)?.nome : "";
        titulo.textContent = nomePlanta || `Imagem #${img.id}`;
        body.appendChild(titulo);
        const dataUpload = document.createElement("p");
        dataUpload.textContent = `Upload: ${formatarData(img.data_upload)}`;
        body.appendChild(dataUpload);

        if (det) {
            const doenca = mapaDoencasPorId.get(det.doenca_id);
            const nomeDoenca = formatarNomeDoenca(doenca?.nome);
            const linhaDoenca = document.createElement("p");
            linhaDoenca.textContent = `Doença: ${nomeDoenca}`;
            body.appendChild(linhaDoenca);
        }

        if (det) {
            const conf = document.createElement("p");
            conf.textContent = `Confiança: ${formatarPercentual(det.porcentagem_confianca)}`;
            body.appendChild(conf);
        }
        card.appendChild(preview);
        card.appendChild(body);
        galeria.appendChild(card);
    });
}

function atualizarUsuarioLogado() {
    const user = carregarSessao();
    const auth = $("authState");
    if (!auth) {
        return;
    }
    if (!user) {
        auth.textContent = "Sessão não autenticada";
        return;
    }
    auth.textContent = `Conectado como ${user.nome}`;
}

async function carregarResumoDashboard() {
    if (!exigirAutenticacao()) {
        return;
    }
    atualizarUsuarioLogado();
    setStatus("Atualizando dados...", "info");
    const respostas = await Promise.allSettled([
        apiGet("/deteccoes/usuario"),
        apiGet("/plantas/usuario"),
        apiGet("/doencas/usuario"),
        apiGet("/recomendacoes/usuario"),
        apiGet("/imagens/usuario")
    ]);

    const [deteccoesRes, plantasRes, doencasRes, recomendacoesRes, imagensRes] =
        respostas;

    let deteccoes = [];
    let plantas = [];
    let doencas = [];
    let recomendacoes = [];
    let imagens = [];

    if (deteccoesRes.status === "fulfilled") {
        deteccoes = deteccoesRes.value || [];
        setText("totalDetecoes", deteccoes.length);
    } else {
        setText("totalDetecoes", "-");
    }

    if (plantasRes.status === "fulfilled") {
        plantas = plantasRes.value || [];
        setText("totalPlantas", plantas.length);
    } else {
        setText("totalPlantas", "-");
    }

    if (doencasRes.status === "fulfilled") {
        doencas = doencasRes.value || [];
        setText("totalDoencas", doencas.length);
    } else {
        setText("totalDoencas", "-");
    }

    if (recomendacoesRes.status === "fulfilled") {
        recomendacoes = recomendacoesRes.value || [];
        setText("totalRecomendacoes", recomendacoes.length);
    } else {
        setText("totalRecomendacoes", "-");
    }

    if (imagensRes.status === "fulfilled") {
        imagens = imagensRes.value || [];
        console.log("[DASHBOARD] APIs retornadas:");
        console.log(`  - Detecções: ${deteccoes.length}`);
        console.log(`  - Plantas: ${plantas.length}`);
        console.log(`  - Doenças: ${doencas.length}`);
        console.log(`  - Recomendações: ${recomendacoes.length}`);
        console.log(`  - Imagens: ${imagens.length}`);
        console.log("[DASHBOARD] Primeiras 3 imagens:");
        imagens.slice(0, 3).forEach((img, idx) => {
            console.log(`  [${idx}] ID=${img.id}, url_imagem='${img.url_imagem}'`);
        });
        setText("totalImagens", imagens.length);
    } else {
        setText("totalImagens", "-");
    }
    renderizarGaleria(imagens, deteccoes, plantas, doencas);
    setStatus("Painel atualizado com sucesso.", "success");
}

window.carregarResumoDashboard = carregarResumoDashboard;

window.addEventListener("DOMContentLoaded", () => {
    const root = $("dashboardPage");
    if (!root) {
        return;
    }
    carregarResumoDashboard().catch((erro) => {
        setStatus(erro.message || "Falha ao carregar o painel.", "error");
    });
});