"""
Tradução do payload JSON recebido do formulário web (wizard) para:
  1. um dicionário de valores prontos para preencher o formulario.pdf
  2. (opcionalmente) os dados da Declaração de Isenção de IR

Toda a validação "de negócio" (campos obrigatórios conforme as escolhas
feitas pelo usuário) acontece aqui, no servidor — o JavaScript do
formulário também valida no navegador, mas o backend nunca confia
apenas nisso.

Dados reaproveitados automaticamente (não são pedidos duas vezes)
-------------------------------------------------------------------
- O titular da conta em cada bloco de crédito (beneficiário ou
  representante legal) é sempre o próprio beneficiário/representante já
  identificado no topo do formulário — o PDF do BB é explícito ("Vedado
  crédito a terceiros"), então não faz sentido perguntar de novo.
- O nome/CPF do declarante na Declaração de Isenção de IR é sempre o do
  beneficiário (é ele quem recebe o rendimento e precisa da isenção),
  reaproveitando os dados já informados no topo do formulário.
"""
from __future__ import annotations

from datetime import date
from typing import Any

from . import field_map as fm
from .declaracao import DadosDeclaracao


def _req(d: dict, key: str, label: str, errors: list[str]) -> str:
    val = (d.get(key) or "").strip()
    if not val:
        errors.append(f"Campo obrigatório não preenchido: {label}")
    return val


def _money_to_decimal_str(value: str) -> str:
    """'1.234,56' ou '1234.56' ou '1234,56' -> '1234.56' (string com ponto)."""
    value = value.strip()
    if not value:
        return ""
    if "," in value:
        value = value.replace(".", "").replace(",", ".")
    return value


def build_formulario_values(
    payload: dict[str, Any]
) -> tuple[dict[str, str], "DadosDeclaracao | None", list[str]]:
    errors: list[str] = []
    values: dict[str, str] = {}

    # --- Identificação -----------------------------------------------------
    quem_preenche = payload.get("quem_preenche")
    if quem_preenche not in ("beneficiario", "procurador"):
        errors.append("Selecione quem está preenchendo o formulário.")

    benef = payload.get("beneficiario") or {}
    benef_nome = _req(benef, "nome", "Nome do beneficiário", errors)
    benef_cpf = _req(benef, "cpf_cnpj", "CPF/CNPJ do beneficiário", errors)
    values[fm.F_BENEF_NOME] = benef_nome
    values[fm.F_BENEF_CPF_CNPJ] = benef_cpf

    # Pessoa jurídica (CNPJ) cujo estatuto exige assinatura de mais de uma
    # pessoa (ex.: presidente e tesoureiro): os nomes e CPFs de todos os
    # assinantes são concatenados, em ordem, no mesmo campo "Representante
    # Legal" do PDF — não há campos próprios no formulário do BB para
    # múltiplos assinantes.
    pj_multiplos = payload.get("beneficiario_pj_multiplos_assinantes") == "sim"

    # Um representante legal/procurador pode estar envolvido mesmo quando é
    # o próprio beneficiário quem preenche o formulário (por exemplo, para
    # receber parte do valor por rateio) — por isso essa condição é
    # independente de "quem está preenchendo". A pessoa jurídica com
    # múltiplos assinantes também conta como representante envolvido.
    representante_envolvido = (
        pj_multiplos
        or quem_preenche == "procurador"
        or payload.get("representante_envolvido") == "sim"
    )

    rep_nome = ""
    rep_cpf = ""
    if pj_multiplos:
        qtd_raw = payload.get("beneficiario_pj_qtd_assinantes")
        if qtd_raw not in ("2", "3"):
            errors.append("Selecione quantas pessoas precisam assinar (2 ou 3).")
            qtd = 2
        else:
            qtd = int(qtd_raw)

        assinantes = payload.get("beneficiario_pj_assinantes") or []
        nomes = []
        cpfs = []
        for i in range(qtd):
            assinante = assinantes[i] if i < len(assinantes) else {}
            if not isinstance(assinante, dict):
                assinante = {}
            nomes.append(_req(assinante, "nome", f"Nome do {i + 1}º assinante", errors))
            cpfs.append(_req(assinante, "cpf", f"CPF do {i + 1}º assinante", errors))
        rep_nome = " | ".join(nomes)
        rep_cpf = " | ".join(cpfs)
        values[fm.F_REP_NOME] = rep_nome
        values[fm.F_REP_CPF_CNPJ] = rep_cpf
    elif representante_envolvido:
        rep = payload.get("representante") or {}
        rep_nome = _req(rep, "nome", "Nome do representante legal/procurador", errors)
        rep_cpf = _req(rep, "cpf_cnpj", "CPF/CNPJ do representante legal/procurador", errors)
        values[fm.F_REP_NOME] = rep_nome
        values[fm.F_REP_CPF_CNPJ] = rep_cpf

    # --- Tipo de depósito ----------------------------------------------------
    tipo_deposito = payload.get("tipo_deposito")
    tipo_map = {
        "estadual": fm.F_TIPO_ESTADUAL,
        "trabalhista": fm.F_TIPO_TRABALHISTA,
        "precatorio": fm.F_TIPO_PRECATORIO,
    }
    if tipo_deposito not in tipo_map:
        errors.append("Selecione o tipo de depósito.")
    else:
        values[tipo_map[tipo_deposito]] = fm.CHECKED

    # --- Conta(s) judicial(ais) ----------------------------------------------
    contas = payload.get("contas_judiciais") or []
    contas = [c.strip() for c in contas if c and c.strip()]
    if not contas:
        errors.append("Informe ao menos uma conta judicial.")
    for field, idx in ((fm.F_CONTA_1, 0), (fm.F_CONTA_2, 1), (fm.F_CONTA_3, 2)):
        if idx < len(contas):
            values[field] = contas[idx]

    # --- Forma de recebimento --------------------------------------------------
    # "credito_dividido" marca simultaneamente os dois checkboxes de
    # crédito (beneficiário + representante legal) — o próprio PDF do BB
    # já prevê valor "Parcial R$ / Percentual %" em cada um dos dois
    # blocos, então dividir o valor entre as duas contas é uma combinação
    # válida dentro do formulário original, não uma extensão criada por
    # esta ferramenta.
    forma = payload.get("forma_recebimento")
    forma_checkbox_map = {
        "autorizacao_permanente": fm.F_FORMA_AUTORIZACAO_PERMANENTE,
        "convenio_djc": fm.F_FORMA_CONVENIO_DJC,
        "credito_beneficiario": fm.F_FORMA_CREDITO_BENEFICIARIO,
        "credito_representante": fm.F_FORMA_CREDITO_REPRESENTANTE,
        "especie": fm.F_FORMA_ESPECIE,
    }
    formas_validas = set(forma_checkbox_map) | {"credito_dividido"}

    if forma not in formas_validas:
        errors.append("Selecione a forma de recebimento dos valores resgatados.")
    elif forma == "credito_dividido":
        values[fm.F_FORMA_CREDITO_BENEFICIARIO] = fm.CHECKED
        values[fm.F_FORMA_CREDITO_REPRESENTANTE] = fm.CHECKED
    else:
        values[forma_checkbox_map[forma]] = fm.CHECKED

    if forma in ("credito_representante", "credito_dividido") and not representante_envolvido:
        errors.append(
            "Crédito para o representante legal (ou divisão entre beneficiário e "
            "representante) só pode ser escolhido quando há um representante "
            "legal/procurador identificado."
        )

    def preencher_bloco_credito(
        dados: dict, prefixo_label: str, F: dict, titular_nome: str, titular_cpf: str
    ):
        values[F["banco_num"]] = _req(dados, "banco_num", f"Banco (nº) — {prefixo_label}", errors)
        values[F["banco_nome"]] = dados.get("banco_nome", "").strip()
        values[F["agencia"]] = _req(dados, "agencia", f"Agência — {prefixo_label}", errors)
        values[F["conta"]] = _req(dados, "conta", f"Conta — {prefixo_label}", errors)
        # Titular = o próprio beneficiário/representante já identificado
        # acima (o PDF veda crédito a terceiros); não é pedido de novo.
        values[F["titular_nome"]] = titular_nome
        values[F["titular_cpf_cnpj"]] = titular_cpf

        tipo_conta = dados.get("tipo_conta")
        if tipo_conta == "corrente":
            values[F["tipo_corrente"]] = fm.CHECKED
        elif tipo_conta == "poupanca":
            values[F["tipo_poupanca"]] = fm.CHECKED
            values[F["poupanca_variacao"]] = dados.get("poupanca_variacao", "").strip()
        else:
            errors.append(f"Selecione o tipo de conta (corrente/poupança) — {prefixo_label}")

        valor_opcao = dados.get("valor_opcao")
        if valor_opcao == "total":
            values[F["valor_total"]] = fm.CHECKED
        elif valor_opcao == "saldo_remanescente":
            values[F["valor_saldo_remanescente"]] = fm.CHECKED
        elif valor_opcao == "fixo":
            values[F["valor_fixo_ck"]] = fm.CHECKED
            values[F["valor_fixo_rs"]] = _req(dados, "valor_fixo", f"Valor fixo (R$) — {prefixo_label}", errors)
        elif valor_opcao == "parcial":
            # O PDF tem checkboxes distintos para "Parcial R$" e
            # "Percentual %" — marcamos cada um conforme o dado informado
            # (podem ser preenchidos os dois, se o usuário quiser).
            valor_parcial_rs = dados.get("valor_parcial", "").strip()
            percentual = dados.get("percentual", "").strip()
            if not valor_parcial_rs and not percentual:
                errors.append(f"Informe o valor parcial (R$) ou o percentual — {prefixo_label}")
            if valor_parcial_rs:
                values[F["valor_parcial_ck"]] = fm.CHECKED
                values[F["valor_parcial_rs"]] = valor_parcial_rs
            if percentual:
                values[F["valor_percentual_ck"]] = fm.CHECKED
                values[F["valor_percentual"]] = percentual
        else:
            errors.append(f"Selecione a opção de valor a resgatar — {prefixo_label}")

    if forma in ("credito_beneficiario", "credito_dividido"):
        dados = payload.get("credito_beneficiario") or {}
        F = dict(
            banco_num=fm.F_BENEF_BANCO_NUM, banco_nome=fm.F_BENEF_BANCO_NOME,
            agencia=fm.F_BENEF_AGENCIA, conta=fm.F_BENEF_CONTA,
            titular_nome=fm.F_BENEF_TITULAR_NOME, titular_cpf_cnpj=fm.F_BENEF_TITULAR_CPF_CNPJ,
            tipo_corrente=fm.F_BENEF_TIPO_CORRENTE, tipo_poupanca=fm.F_BENEF_TIPO_POUPANCA,
            poupanca_variacao=fm.F_BENEF_POUPANCA_VARIACAO,
            valor_total=fm.F_BENEF_VALOR_TOTAL, valor_saldo_remanescente=fm.F_BENEF_VALOR_SALDO_REMANESCENTE,
            valor_fixo_ck=fm.F_BENEF_VALOR_FIXO_CK, valor_fixo_rs=fm.F_BENEF_VALOR_FIXO_RS,
            valor_parcial_ck=fm.F_BENEF_VALOR_PARCIAL_CK, valor_parcial_rs=fm.F_BENEF_VALOR_PARCIAL_RS,
            valor_percentual_ck=fm.F_BENEF_VALOR_PERCENTUAL_CK, valor_percentual=fm.F_BENEF_VALOR_PERCENTUAL,
        )
        preencher_bloco_credito(dados, "dados bancários do beneficiário", F, benef_nome, benef_cpf)

    if forma in ("credito_representante", "credito_dividido"):
        dados = payload.get("credito_representante") or {}
        F = dict(
            banco_num=fm.F_REP_BANCO_NUM, banco_nome=fm.F_REP_BANCO_NOME,
            agencia=fm.F_REP_AGENCIA, conta=fm.F_REP_CONTA,
            titular_nome=fm.F_REP_TITULAR_NOME, titular_cpf_cnpj=fm.F_REP_TITULAR_CPF_CNPJ,
            tipo_corrente=fm.F_REP_TIPO_CORRENTE, tipo_poupanca=fm.F_REP_TIPO_POUPANCA,
            poupanca_variacao=fm.F_REP_POUPANCA_VARIACAO,
            valor_total=fm.F_REP_VALOR_TOTAL, valor_saldo_remanescente=fm.F_REP_VALOR_SALDO_REMANESCENTE,
            valor_fixo_ck=fm.F_REP_VALOR_FIXO_CK, valor_fixo_rs=fm.F_REP_VALOR_FIXO_RS,
            valor_parcial_ck=fm.F_REP_VALOR_PARCIAL_CK, valor_parcial_rs=fm.F_REP_VALOR_PARCIAL_RS,
            valor_percentual_ck=fm.F_REP_VALOR_PERCENTUAL_CK, valor_percentual=fm.F_REP_VALOR_PERCENTUAL,
        )
        preencher_bloco_credito(dados, "dados bancários do representante legal", F, rep_nome, rep_cpf)

    if forma == "especie":
        especie = payload.get("especie") or {}
        prefixo = especie.get("prefixo_agencia", "").strip()
        if prefixo:
            values[fm.F_ESPECIE_PREFIXO_AGENCIA] = prefixo

    # --- Imposto de renda --------------------------------------------------
    declaracao_dados: DadosDeclaracao | None = None
    if tipo_deposito == "precatorio":
        ir = payload.get("ir") or {}
        isento = ir.get("isento")
        if isento == "sim":
            values[fm.F_IR_ISENTO_SIM] = fm.CHECKED
        elif isento == "nao":
            values[fm.F_IR_ISENTO_NAO] = fm.CHECKED
        else:
            errors.append("Informe se o beneficiário é isento de imposto de renda.")

        if isento == "sim":
            decl = ir.get("declaracao") or {}
            tipo_decl = decl.get("tipo", "isento")
            # Nome/CPF do declarante = os mesmos do beneficiário informados
            # no topo do formulário (não pedidos de novo).
            endereco_decl = _req(decl, "endereco", "Endereço (declaração de isenção)", errors)
            processo_decl = _req(decl, "numero_processo", "Número do processo (declaração de isenção)", errors)
            vara_decl = _req(decl, "vara", "Vara/seção judiciária (declaração de isenção)", errors)
            municipio_decl = _req(decl, "municipio", "Município (declaração de isenção)", errors)

            valor_decl = None
            if tipo_decl == "isento":
                valor_raw = _req(decl, "valor", "Valor a receber (declaração de isenção)", errors)
                valor_decl = _money_to_decimal_str(valor_raw)
                if valor_decl:
                    try:
                        float(valor_decl)
                    except ValueError:
                        errors.append("Valor a receber (declaração de isenção) inválido.")
                        valor_decl = None

            # O local e a data da assinatura da declaração são os mesmos já
            # informados em "Local e Data" no final do formulário principal
            # (não são pedidos de novo, e não devem ser confundidos com o
            # município do processo, usado só no corpo do texto).
            local_data_payload = payload.get("local_data") or {}
            local_assinatura = local_data_payload.get("local", "").strip()
            data_str = local_data_payload.get("data", "").strip()
            data_decl = None
            if data_str:
                try:
                    data_decl = date.fromisoformat(data_str)
                except ValueError:
                    pass  # erro já será reportado na validação de "Local e Data" mais abaixo
            if not data_decl:
                data_decl = date.today()

            declaracao_dados = DadosDeclaracao(
                nome=benef_nome,
                cpf_cnpj=benef_cpf,
                endereco=endereco_decl,
                numero_processo=processo_decl,
                vara=vara_decl,
                municipio=municipio_decl,
                tipo=tipo_decl,
                local_assinatura=local_assinatura,
                valor=valor_decl,
                data=data_decl,
            )

    # --- Beneficiário analfabeto --------------------------------------------
    analf = payload.get("analfabeto") or {}
    resposta = analf.get("resposta")
    if resposta == "sim":
        values[fm.F_ANALFABETO_SIM] = fm.CHECKED
        modo = analf.get("modo")
        if modo == "testemunhas":
            # O PDF atual já traz campos preenchíveis para as duas
            # testemunhas (antes eram apenas linhas para assinatura à
            # mão). Mesmo assim, o preenchimento continua opcional aqui —
            # quem preferir pode simplesmente assinar à mão no documento
            # impresso, como já era possível antes.
            test = analf.get("testemunhas") or {}
            values[fm.F_TESTEMUNHA1_NOME] = test.get("testemunha1_nome", "").strip()
            values[fm.F_TESTEMUNHA1_CPF] = test.get("testemunha1_cpf", "").strip()
            values[fm.F_TESTEMUNHA2_NOME] = test.get("testemunha2_nome", "").strip()
            values[fm.F_TESTEMUNHA2_CPF] = test.get("testemunha2_cpf", "").strip()
        elif modo == "rogo":
            rogo = analf.get("rogo") or {}
            signer_nome = _req(rogo, "signer_nome", "Nome de quem assina a rogo", errors)
            signer_cpf = _req(rogo, "signer_cpf", "CPF de quem assina a rogo", errors)
            values[fm.F_ROGO_SIGNER_NOME] = signer_nome
            values[fm.F_ROGO_SIGNER_RG_NUM] = _req(rogo, "signer_rg_num", "RG de quem assina a rogo", errors)
            values[fm.F_ROGO_SIGNER_RG_ORGAO] = rogo.get("signer_rg_orgao", "").strip()
            values[fm.F_ROGO_SIGNER_RG_DATA] = rogo.get("signer_rg_data", "").strip()
            values[fm.F_ROGO_SIGNER_CPF] = signer_cpf
            values[fm.F_ROGO_BENEF_NOME] = _req(rogo, "benef_nome", "Nome do beneficiário analfabeto", errors)
            values[fm.F_ROGO_BENEF_RG_NUM] = _req(rogo, "benef_rg_num", "RG do beneficiário analfabeto", errors)
            values[fm.F_ROGO_BENEF_RG_ORGAO] = rogo.get("benef_rg_orgao", "").strip()
            values[fm.F_ROGO_BENEF_RG_DATA] = rogo.get("benef_rg_data", "").strip()
            values[fm.F_ROGO_ALVARA_NUM] = _req(rogo, "alvara_num", "Número do Alvará Judicial", errors)
            # Nome/CPF impressos sob a linha de assinatura = os mesmos de
            # quem assina a rogo (não pedidos de novo).
            values[fm.F_ROGO_SIGNER_PRINTED_NOME] = signer_nome
            values[fm.F_ROGO_SIGNER_PRINTED_CPF] = signer_cpf
            # Testemunhas do termo "a rogo" — o PDF pede duas, distintas
            # das testemunhas do método direto, mas também opcionais aqui
            # (podem ser preenchidas à mão no documento impresso).
            rogo_test = rogo.get("testemunhas") or {}
            values[fm.F_ROGO_TESTEMUNHA1_NOME] = rogo_test.get("testemunha1_nome", "").strip()
            values[fm.F_ROGO_TESTEMUNHA1_CPF] = rogo_test.get("testemunha1_cpf", "").strip()
            values[fm.F_ROGO_TESTEMUNHA2_NOME] = rogo_test.get("testemunha2_nome", "").strip()
            values[fm.F_ROGO_TESTEMUNHA2_CPF] = rogo_test.get("testemunha2_cpf", "").strip()
        else:
            errors.append("Selecione como será assinado o levantamento (testemunhas ou termo a rogo).")
    elif resposta == "nao":
        values[fm.F_ANALFABETO_NAO] = fm.CHECKED
    else:
        errors.append("Informe se o beneficiário é analfabeto.")

    # --- Contato -------------------------------------------------------------
    contato = payload.get("contato") or {}
    values[fm.F_TEL_DDD] = contato.get("tel_ddd", "").strip()
    values[fm.F_TEL_NUM] = contato.get("tel_num", "").strip()
    values[fm.F_CEL_DDD] = contato.get("cel_ddd", "").strip()
    values[fm.F_CEL_NUM] = contato.get("cel_num", "").strip()
    values[fm.F_EMAIL] = contato.get("email", "").strip()
    if not (values[fm.F_TEL_NUM] or values[fm.F_CEL_NUM]):
        errors.append("Informe ao menos um telefone (fixo ou celular) para contato.")

    # --- Local e data ----------------------------------------------------------
    local_data = payload.get("local_data") or {}
    values[fm.F_LOCAL] = _req(local_data, "local", "Local (cidade/UF)", errors)
    data_str = local_data.get("data", "").strip()
    if data_str:
        try:
            d = date.fromisoformat(data_str)
            values[fm.F_DATA_DIA] = str(d.day)
            values[fm.F_DATA_MES] = fm.MESES_PT[d.month]
            values[fm.F_DATA_ANO] = str(d.year)
        except (ValueError, KeyError):
            errors.append("Data (Local e Data) inválida.")
    else:
        errors.append("Informe a data do formulário.")

    # Remove valores vazios para não sobrescrever campos opcionais com ""
    # de forma desnecessária (mantemos apenas o que tem conteúdo real ou é
    # um checkbox já tratado acima).
    values = {k: v for k, v in values.items() if v not in (None, "")}

    return values, declaracao_dados, errors
