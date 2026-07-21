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
  const wrapRepresentanteToggle = document.getElementById("wrap-representante-toggle");
  const chkRepresentanteEnvolvido = document.getElementById("chk-representante-envolvido");
  const wrapPjMultiplos = document.getElementById("wrap-pj-multiplos");
  const blocoPjQuantidade = document.getElementById("bloco-pj-quantidade");
  const blocoPjAssinante3 = document.getElementById("bloco-pj-assinante-3");
  const opcaoCreditoRepresentante = document.getElementById("opcao-credito-representante");
  const opcaoCreditoDividido = document.getElementById("opcao-credito-dividido");
  const hintDividido = document.getElementById("hint-dividido");
  const blocoBancoBeneficiario = document.getElementById("bloco-banco-beneficiario");
  const blocoBancoRepresentante = document.getElementById("bloco-banco-representante");
  const blocoEspecie = document.getElementById("bloco-especie");
  const blocoIR = document.getElementById("bloco-ir");
  const blocoDeclaracaoIsencao = document.getElementById("bloco-declaracao-isencao");
  const blocoValorIsencao = document.getElementById("bloco-valor-isencao");
  const blocoAnalfabeto = document.getElementById("bloco-analfabeto");
  const blocoRogo = document.getElementById("bloco-rogo");
  const blocoTestemunhasDiretas = document.getElementById("bloco-testemunhas-diretas");

  function radioValue(name) {
    const el = form.querySelector(`input[name="${name}"]:checked`);
    return el ? el.value : null;
  }

  function pjMultiplosAtivo() {
    return radioValue("beneficiario_pj_multiplos_assinantes") === "sim";
  }

  // Um representante legal/procurador pode estar envolvido mesmo quando é
  // o próprio beneficiário quem preenche o formulário (ex.: para receber
  // parte do valor por rateio) — por isso essa condição é independente de
  // "quem está preenchendo". A pessoa jurídica com múltiplos assinantes
  // também conta como representante envolvido (os nomes/CPFs vão para o
  // mesmo campo "Representante Legal" do PDF).
  function representanteEnvolvido() {
    if (pjMultiplosAtivo()) return true;
    if (radioValue("quem_preenche") === "procurador") return true;
    return chkRepresentanteEnvolvido.checked;
  }

  function atualizarBeneficiarioPJ() {
    const cpfCnpjInput = form.querySelector('input[name="beneficiario.cpf_cnpj"]');
    const digits = (cpfCnpjInput.value || "").replace(/\D/g, "");
    const isCnpj = digits.length === 14;
    setVisible(wrapPjMultiplos, isCnpj);
    if (!isCnpj) {
      const radioNao = form.querySelector('input[name="beneficiario_pj_multiplos_assinantes"][value="nao"]');
      if (radioNao) radioNao.checked = true;
    }
    atualizarPjMultiplos();
  }

  function atualizarPjMultiplos() {
    setVisible(blocoPjQuantidade, pjMultiplosAtivo());
    atualizarPjQuantidade();
    atualizarQuemPreenche();
  }

  function atualizarPjQuantidade() {
    const qtd = radioValue("beneficiario_pj_qtd_assinantes") || "2";
    setVisible(blocoPjAssinante3, qtd === "3");
  }

  function atualizarQuemPreenche() {
    const isProcurador = radioValue("quem_preenche") === "procurador";
    const multiplos = pjMultiplosAtivo();
    setVisible(wrapRepresentanteToggle, !isProcurador && !multiplos);
    if (isProcurador) chkRepresentanteEnvolvido.checked = true;
    atualizarRepresentanteVisibility();
  }

  function atualizarRepresentanteVisibility() {
    const envolvido = representanteEnvolvido();
    const multiplos = pjMultiplosAtivo();
    setVisible(blocoRepresentante, envolvido && !multiplos);
    setVisible(opcaoCreditoRepresentante, envolvido);
    setVisible(opcaoCreditoDividido, envolvido);
    if (!envolvido) {
      ["credito_representante", "credito_dividido"].forEach((val) => {
        const radio = form.querySelector(`input[name="forma_recebimento"][value="${val}"]`);
        if (radio && radio.checked) radio.checked = false;
      });
      atualizarFormaRecebimento();
    }
  }

  function atualizarTipoDeposito() {
    const v = radioValue("tipo_deposito");
    setVisible(blocoIR, v === "precatorio");
  }

  function atualizarFormaRecebimento() {
    const v = radioValue("forma_recebimento");
    setVisible(blocoBancoBeneficiario, v === "credito_beneficiario" || v === "credito_dividido");
    setVisible(blocoBancoRepresentante, v === "credito_representante" || v === "credito_dividido");
    setVisible(blocoEspecie, v === "especie");
    setVisible(hintDividido, v === "credito_dividido");
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
    setVisible(blocoTestemunhasDiretas, v === "testemunhas");
  }

  form.addEventListener("change", (ev) => {
    const name = ev.target.name;
    if (name === "quem_preenche") atualizarQuemPreenche();
    if (name === "representante_envolvido") atualizarRepresentanteVisibility();
    if (name === "beneficiario_pj_multiplos_assinantes") atualizarPjMultiplos();
    if (name === "beneficiario_pj_qtd_assinantes") atualizarPjQuantidade();
    if (name === "tipo_deposito") atualizarTipoDeposito();
    if (name === "forma_recebimento") atualizarFormaRecebimento();
    if (name === "ir.isento") atualizarIsencao();
    if (name === "ir.declaracao.tipo") atualizarTipoDeclaracao();
    if (name === "analfabeto.resposta") atualizarAnalfabeto();
    if (name === "analfabeto.modo") atualizarModoAnalfabeto();
  });

  form.querySelector('input[name="beneficiario.cpf_cnpj"]').addEventListener("input", atualizarBeneficiarioPJ);

  // Estado inicial
  atualizarBeneficiarioPJ();
  atualizarQuemPreenche();
  atualizarTipoDeposito();
  atualizarFormaRecebimento();
  atualizarIsencao();
  atualizarTipoDeclaracao();
  atualizarAnalfabeto();
  atualizarModoAnalfabeto();

  // ---------------------------------------------------------------------
  // Máscaras de entrada: CPF/CNPJ e número de processo (padrão CNJ)
  // ---------------------------------------------------------------------
  function applyMask(digits, template) {
    let result = "";
    let di = 0;
    for (const ch of template) {
      if (di >= digits.length) break;
      if (ch === "#") {
        result += digits[di++];
      } else {
        result += ch;
      }
    }
    return result;
  }

  function formatCpfCnpj(rawDigits) {
    const digits = rawDigits.slice(0, 14);
    if (digits.length <= 11) {
      return applyMask(digits, "###.###.###-##");
    }
    return applyMask(digits, "##.###.###/####-##");
  }

  function formatProcesso(rawDigits) {
    const digits = rawDigits.slice(0, 20);
    return applyMask(digits, "#######-##.####.#.##.####");
  }

  const MASK_FORMATTERS = {
    cpf_cnpj: formatCpfCnpj,
    processo: formatProcesso,
  };

  function initMasks() {
    form.querySelectorAll("[data-mask]").forEach((input) => {
      const formatter = MASK_FORMATTERS[input.dataset.mask];
      if (!formatter) return;
      input.addEventListener("input", () => {
        const digits = input.value.replace(/\D/g, "");
        input.value = formatter(digits);
      });
    });
  }
  initMasks();

  // ---------------------------------------------------------------------
  // Combobox de busca de bancos (código + nome)
  // ---------------------------------------------------------------------
  function normalizeText(s) {
    return s
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");
  }

  function initBankCombobox(container) {
    const searchInput = container.querySelector("[data-bank-search]");
    const dropdown = container.querySelector("[data-bank-dropdown]");
    const numInput = container.querySelector("[data-bank-num]");
    const nomeInput = container.querySelector("[data-bank-nome]");
    const searchWrap = container.querySelector("[data-bank-search-wrap]");
    const manualWrap = container.querySelector("[data-bank-manual-wrap]");
    const toggleBtn = container.querySelector("[data-bank-toggle]");
    const bancos = window.BANCOS_BR || [];

    function setManualMode(manual) {
      setVisible(manualWrap, manual);
      setVisible(searchWrap, !manual);
      toggleBtn.textContent = manual
        ? "Usar a busca de banco"
        : "Meu banco não está na lista — preencher manualmente";
    }
    setManualMode(false);
    toggleBtn.addEventListener("click", () => {
      const isManual = !manualWrap.classList.contains("hidden");
      setManualMode(!isManual);
    });

    function renderResults(query) {
      const normQuery = normalizeText(query.trim());
      dropdown.innerHTML = "";
      if (!normQuery) {
        hide(dropdown);
        return;
      }
      const results = bancos
        .filter((b) => b.codigo.startsWith(normQuery) || normalizeText(b.nome).includes(normQuery))
        .slice(0, 8);

      if (!results.length) {
        hide(dropdown);
        return;
      }

      results.forEach((b) => {
        const li = document.createElement("li");
        li.textContent = `${b.codigo} — ${b.nome}`;
        li.tabIndex = -1;
        li.addEventListener("mousedown", (ev) => {
          // mousedown (em vez de click) dispara antes do blur do input
          ev.preventDefault();
          numInput.value = b.codigo;
          nomeInput.value = b.nome;
          searchInput.value = `${b.codigo} — ${b.nome}`;
          hide(dropdown);
        });
        dropdown.appendChild(li);
      });
      show(dropdown);
    }

    searchInput.addEventListener("input", () => renderResults(searchInput.value));
    searchInput.addEventListener("focus", () => {
      if (searchInput.value.trim()) renderResults(searchInput.value);
    });
    searchInput.addEventListener("blur", () => {
      setTimeout(() => hide(dropdown), 100);
    });
  }

  form.querySelectorAll("[data-bank-combobox]").forEach(initBankCombobox);

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
