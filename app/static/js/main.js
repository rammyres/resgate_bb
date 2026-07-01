(function () {
  "use strict";

  const form = document.getElementById("wizard-form");
  const btn = document.getElementById("btn-gerar");
  const statusMsg = document.getElementById("status-msg");
  const errorsBox = document.getElementById("form-errors");

  // ---------------------------------------------------------------------
  // Helpers de exibição condicional
  // ---------------------------------------------------------------------
  function show(el) { el.classList.remove("hidden"); }
  function hide(el) { el.classList.add("hidden"); }
  function setVisible(el, visible) { visible ? show(el) : hide(el); }

  const blocoRepresentante = document.getElementById("bloco-representante");
  const opcaoCreditoRepresentante = document.getElementById("opcao-credito-representante");
  const blocoBancoBeneficiario = document.getElementById("bloco-banco-beneficiario");
  const blocoBancoRepresentante = document.getElementById("bloco-banco-representante");
  const blocoEspecie = document.getElementById("bloco-especie");
  const blocoIR = document.getElementById("bloco-ir");
  const blocoDeclaracaoIsencao = document.getElementById("bloco-declaracao-isencao");
  const blocoValorIsencao = document.getElementById("bloco-valor-isencao");
  const blocoAnalfabeto = document.getElementById("bloco-analfabeto");
  const blocoRogo = document.getElementById("bloco-rogo");

  function radioValue(name) {
    const el = form.querySelector(`input[name="${name}"]:checked`);
    return el ? el.value : null;
  }

  function atualizarQuemPreenche() {
    const v = radioValue("quem_preenche");
    const isProcurador = v === "procurador";
    setVisible(blocoRepresentante, isProcurador);
    setVisible(opcaoCreditoRepresentante, isProcurador);
    if (!isProcurador) {
      const radioRep = form.querySelector('input[name="forma_recebimento"][value="credito_representante"]');
      if (radioRep && radioRep.checked) radioRep.checked = false;
      atualizarFormaRecebimento();
    }
  }

  function atualizarTipoDeposito() {
    const v = radioValue("tipo_deposito");
    setVisible(blocoIR, v === "precatorio");
  }

  function atualizarFormaRecebimento() {
    const v = radioValue("forma_recebimento");
    setVisible(blocoBancoBeneficiario, v === "credito_beneficiario");
    setVisible(blocoBancoRepresentante, v === "credito_representante");
    setVisible(blocoEspecie, v === "especie");
  }

  function atualizarIsencao() {
    const v = radioValue("ir.isento");
    setVisible(blocoDeclaracaoIsencao, v === "sim");
  }

  function atualizarTipoDeclaracao() {
    const v = radioValue("ir.declaracao.tipo");
    setVisible(blocoValorIsencao, v === "isento");
  }

  function atualizarAnalfabeto() {
    const v = radioValue("analfabeto.resposta");
    setVisible(blocoAnalfabeto, v === "sim");
  }

  function atualizarModoAnalfabeto() {
    const v = radioValue("analfabeto.modo");
    setVisible(blocoRogo, v === "rogo");
  }

  form.addEventListener("change", (ev) => {
    const name = ev.target.name;
    if (name === "quem_preenche") atualizarQuemPreenche();
    if (name === "tipo_deposito") atualizarTipoDeposito();
    if (name === "forma_recebimento") atualizarFormaRecebimento();
    if (name === "ir.isento") atualizarIsencao();
    if (name === "ir.declaracao.tipo") atualizarTipoDeclaracao();
    if (name === "analfabeto.resposta") atualizarAnalfabeto();
    if (name === "analfabeto.modo") atualizarModoAnalfabeto();
  });

  // Estado inicial
  atualizarQuemPreenche();
  atualizarTipoDeposito();
  atualizarFormaRecebimento();
  atualizarIsencao();
  atualizarTipoDeclaracao();
  atualizarAnalfabeto();
  atualizarModoAnalfabeto();

  // ---------------------------------------------------------------------
  // Construção do payload aninhado a partir dos campos "a.b.c" / "a.0"
  // ---------------------------------------------------------------------
  function setPath(obj, path, value) {
    const parts = path.split(".");
    let cur = obj;
    for (let i = 0; i < parts.length; i++) {
      const part = parts[i];
      const isLast = i === parts.length - 1;
      const isIndex = /^\d+$/.test(part);
      const key = isIndex ? Number(part) : part;

      if (isLast) {
        cur[key] = value;
      } else {
        const nextIsIndex = /^\d+$/.test(parts[i + 1]);
        if (cur[key] === undefined) {
          cur[key] = nextIsIndex ? [] : {};
        }
        cur = cur[key];
      }
    }
  }

  function buildPayload() {
    const data = {};
    const seenRadioGroups = new Set();
    for (const el of form.elements) {
      if (!el.name) continue;
      if (el.disabled) continue;
      if (el.type === "radio") {
        if (!el.checked) continue;
      }
      if (el.type === "checkbox" && !el.checked) continue;
      if (!el.value) continue;
      setPath(data, el.name, el.value);
    }
    return data;
  }

  // ---------------------------------------------------------------------
  // Envio
  // ---------------------------------------------------------------------
  function mostrarErros(lista) {
    errorsBox.innerHTML = "";
    if (!lista || !lista.length) {
      hide(errorsBox);
      return;
    }
    const title = document.createElement("strong");
    title.textContent = "Corrija os itens abaixo antes de gerar o PDF:";
    const ul = document.createElement("ul");
    lista.forEach((msg) => {
      const li = document.createElement("li");
      li.textContent = msg;
      ul.appendChild(li);
    });
    errorsBox.appendChild(title);
    errorsBox.appendChild(ul);
    show(errorsBox);
    errorsBox.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  form.addEventListener("submit", async (ev) => {
    ev.preventDefault();

    if (!form.reportValidity()) {
      return;
    }

    mostrarErros(null);
    btn.disabled = true;
    statusMsg.textContent = "Gerando PDF...";
    statusMsg.className = "status-msg";

    const payload = buildPayload();

    try {
      const resp = await fetch("/api/gerar-pdf", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (resp.status === 422) {
        const body = await resp.json();
        mostrarErros(body.erros || ["Há campos pendentes de preenchimento."]);
        statusMsg.textContent = "";
        return;
      }

      if (!resp.ok) {
        const text = await resp.text();
        throw new Error(`Erro do servidor (${resp.status}): ${text}`);
      }

      const blob = await resp.blob();
      const disposition = resp.headers.get("Content-Disposition") || "";
      const match = disposition.match(/filename="?([^"]+)"?/);
      const filename = match ? match[1] : "formulario_resgate.pdf";

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);

      statusMsg.textContent = "PDF gerado com sucesso.";
      statusMsg.className = "status-msg ok";
    } catch (err) {
      console.error(err);
      statusMsg.textContent = "Não foi possível gerar o PDF. Tente novamente.";
      statusMsg.className = "status-msg err";
    } finally {
      btn.disabled = false;
    }
  });
})();
