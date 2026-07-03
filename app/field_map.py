"""
Mapeamento dos campos do AcroForm do formulario.pdf (Banco do Brasil -
Solicitação de Resgate de Depósito Judicial / Precatório).

Este mapeamento foi construído extraindo a posição (rect) de cada widget
no PDF e ordenando por página/coluna/linha para reconstruir a ordem de
leitura do formulário, cruzando com o texto das etiquetas impressas.
Foi validado preenchendo um conjunto de valores de teste e conferindo
programaticamente (via widget.field_value) que cada campo recebeu o
valor esperado, sem colisões — a contagem final bate exatamente com o
total de 83 campos do PDF (61 na página 1, 22 na página 2).

Observação importante sobre os nomes dos campos
--------------------------------------------------
Os nomes de alguns campos deste PDF contêm literalmente sequências como
"#C3#A7" no lugar de caracteres acentuados (ex.: o campo do checkbox de
"Depósito Estadual" se chama, ao pé da letra,
"Dep#C3#B3sito Estaual" dentro do PDF — não é um artefato de exibição,
é o nome real gravado no arquivo, incluindo um erro de digitação
("Estaual" em vez de "Estadual")). Usamos aqui exatamente essas strings,
copiadas do /T de cada widget.

Todas as caixas de seleção (checkboxes) usam '/Yes' para marcado e '/Off'
para desmarcado.
"""

# ---------------------------------------------------------------------------
# Página 1
# ---------------------------------------------------------------------------

# Identificação
F_BENEF_NOME = "Caixa de texto 2"
F_BENEF_CPF_CNPJ = "Caixa de texto 1"
F_REP_NOME = "Caixa de texto 2_2"
F_REP_CPF_CNPJ = "Caixa de texto 1_2"

# Tipo de depósito (checkboxes mutuamente exclusivos)
F_TIPO_ESTADUAL = "Dep#C3#B3sito Estaual"
F_TIPO_TRABALHISTA = "Dep#C3#B3sito Trabalhista"
F_TIPO_PRECATORIO = "Precat#C3#B3rio ou RPV Federal"

# Conta(s) judicial(ais) - até 3 campos
F_CONTA_1 = "Caixa de texto 2_3"
F_CONTA_2 = "Caixa de texto 2_4"
F_CONTA_3 = "Caixa de texto 2_5"

# Forma de recebimento (checkboxes mutuamente exclusivos)
F_FORMA_AUTORIZACAO_PERMANENTE = "Autoriza#C3#A7#C3#A3o permanente para cr#C3#A9dito em conta do benefici#C3#A1rio no Banco do Brasil"
F_FORMA_CONVENIO_DJC = "Conv#C3#AAnio de Resgate Centralizado - DJC"
F_FORMA_CREDITO_BENEFICIARIO = "CR#C3#89DITO em Conta BB ou TED para o BENEFICI#C3#81RIO"
F_FORMA_CREDITO_REPRESENTANTE = "CR#C3#89DITO Conta BB ou TED para o REPRESENTANTE LEGAL"
F_FORMA_ESPECIE = "unnamed1"

# Bloco "Crédito em Conta BB ou TED para o BENEFICIÁRIO"
F_BENEF_BANCO_NUM = "Caixa de texto 2_6"
F_BENEF_BANCO_NOME = "Caixa de texto 2_7"
F_BENEF_AGENCIA = "Caixa de texto 2_8"
F_BENEF_CONTA = "Caixa de texto 2_9"
F_BENEF_TITULAR_NOME = "Caixa de texto 2_10"
F_BENEF_TITULAR_CPF_CNPJ = "Caixa de texto 2_11"
F_BENEF_TIPO_CORRENTE = "fixo_2"
F_BENEF_TIPO_POUPANCA = "fixo_3"
F_BENEF_POUPANCA_VARIACAO = "Caixa de texto 2_12"
F_BENEF_VALOR_TOTAL = "fixo_4"
F_BENEF_VALOR_SALDO_REMANESCENTE = "fixo_5"
F_BENEF_VALOR_FIXO_CK = "fixo"
F_BENEF_VALOR_FIXO_RS = "Caixa de texto 2_13"
F_BENEF_VALOR_PARCIAL_CK = "Caixa de sele#C3#A7#C3#A3o 1"
F_BENEF_VALOR_PARCIAL_RS = "Caixa de texto 2_14"
F_BENEF_VALOR_PERCENTUAL_CK = "Parcial"
F_BENEF_VALOR_PERCENTUAL = "Caixa de texto 3"

# Bloco "Crédito Conta BB ou TED para o REPRESENTANTE LEGAL"
F_REP_BANCO_NUM = "Caixa de texto 2_25"
F_REP_BANCO_NOME = "Caixa de texto 2_26"
F_REP_AGENCIA = "Caixa de texto 2_27"
F_REP_CONTA = "Caixa de texto 2_28"
F_REP_TITULAR_NOME = "Caixa de texto 2_31"
F_REP_TITULAR_CPF_CNPJ = "Caixa de texto 2_32"
F_REP_TIPO_CORRENTE = "fixo_7"
F_REP_TIPO_POUPANCA = "fixo_8"
F_REP_POUPANCA_VARIACAO = "Caixa de texto 2_33"
F_REP_VALOR_TOTAL = "fixo_9"
F_REP_VALOR_SALDO_REMANESCENTE = "fixo_10"
F_REP_VALOR_FIXO_CK = "fixo_6"
F_REP_VALOR_FIXO_RS = "Caixa de texto 2_29"
F_REP_VALOR_PARCIAL_CK = "Caixa de sele#C3#A7#C3#A3o 1_2"
F_REP_VALOR_PARCIAL_RS = "Caixa de texto 2_30"
F_REP_VALOR_PERCENTUAL_CK = "Parcial_2"
F_REP_VALOR_PERCENTUAL = "Caixa de texto 3_2"

# Pagamento em espécie
F_ESPECIE_PREFIXO_AGENCIA = "Caixa de texto 2_24"

# Imposto de renda
F_IR_ISENTO_SIM = "unnamed0"
F_IR_ISENTO_NAO = "unnamed0_2"

# Contato
F_TEL_DDD = "Caixa de texto 2_15"
F_TEL_NUM = "Caixa de texto 2_16"
F_CEL_DDD = "Caixa de texto 2_17"
F_CEL_NUM = "Caixa de texto 2_18"
F_EMAIL = "Caixa de texto 2_19"

# Local e data
F_LOCAL = "Caixa de texto 2_20"
F_DATA_DIA = "Caixa de texto 2_21"
F_DATA_MES = "Caixa de texto 2_22"
F_DATA_ANO = "Caixa de texto 2_23"

# ---------------------------------------------------------------------------
# Página 2 - Beneficiário analfabeto
# ---------------------------------------------------------------------------

F_ANALFABETO_SIM = "unnamed0_3"
F_ANALFABETO_NAO = "unnamed0_4"

# Método 1: duas testemunhas (agora com campos preenchíveis no PDF; antes
# eram só linhas para assinatura à mão)
F_TESTEMUNHA1_NOME = "Caixa de texto 2_34"
F_TESTEMUNHA2_NOME = "Caixa de texto 2_35"
F_TESTEMUNHA1_CPF = "Caixa de texto 2_45"
F_TESTEMUNHA2_CPF = "Caixa de texto 2_46"

# Método 2: termo de quitação "a rogo" — quem assina
F_ROGO_SIGNER_NOME = "Caixa de texto 2_36"
F_ROGO_SIGNER_RG_NUM = "Caixa de texto 2_37"
F_ROGO_SIGNER_RG_ORGAO = "Caixa de texto 2_38"
F_ROGO_SIGNER_RG_DATA = "Caixa de texto 2_39"
F_ROGO_SIGNER_CPF = "Caixa de texto 2_47"

# Dados do beneficiário analfabeto (a rogo de quem)
F_ROGO_BENEF_NOME = "Caixa de texto 2_40"
F_ROGO_BENEF_RG_NUM = "Caixa de texto 2_41"
F_ROGO_BENEF_RG_ORGAO = "Caixa de texto 2_42"
F_ROGO_BENEF_RG_DATA = "Caixa de texto 2_43"
F_ROGO_ALVARA_NUM = "Caixa de texto 2_44"

# Nome/CPF impressos sob a linha de assinatura de quem assina a rogo
# (duplicam signer_nome/signer_cpf — preenchidos automaticamente com o
# mesmo valor, sem perguntar de novo)
F_ROGO_SIGNER_PRINTED_NOME = "Caixa de texto 2_48"
F_ROGO_SIGNER_PRINTED_CPF = "Caixa de texto 2_49"

# Testemunhas do termo "a rogo" (distintas das testemunhas do método 1)
F_ROGO_TESTEMUNHA1_NOME = "Caixa de texto 2_52"
F_ROGO_TESTEMUNHA2_NOME = "Caixa de texto 2_53"
F_ROGO_TESTEMUNHA1_CPF = "Caixa de texto 2_50"
F_ROGO_TESTEMUNHA2_CPF = "Caixa de texto 2_51"

CHECKED = "/Yes"
UNCHECKED = "/Off"

ALL_CHECKBOX_FIELDS = {
    F_TIPO_ESTADUAL, F_TIPO_TRABALHISTA, F_TIPO_PRECATORIO,
    F_FORMA_AUTORIZACAO_PERMANENTE, F_FORMA_CONVENIO_DJC,
    F_FORMA_CREDITO_BENEFICIARIO, F_FORMA_CREDITO_REPRESENTANTE,
    F_FORMA_ESPECIE,
    F_BENEF_TIPO_CORRENTE, F_BENEF_TIPO_POUPANCA,
    F_BENEF_VALOR_TOTAL, F_BENEF_VALOR_SALDO_REMANESCENTE,
    F_BENEF_VALOR_FIXO_CK, F_BENEF_VALOR_PARCIAL_CK, F_BENEF_VALOR_PERCENTUAL_CK,
    F_REP_TIPO_CORRENTE, F_REP_TIPO_POUPANCA,
    F_REP_VALOR_TOTAL, F_REP_VALOR_SALDO_REMANESCENTE,
    F_REP_VALOR_FIXO_CK, F_REP_VALOR_PARCIAL_CK, F_REP_VALOR_PERCENTUAL_CK,
    F_IR_ISENTO_SIM, F_IR_ISENTO_NAO,
    F_ANALFABETO_SIM, F_ANALFABETO_NAO,
}

# field_id -> página (1-based) no PDF original
FIELD_PAGE = {}
for _name in [
    F_BENEF_NOME, F_BENEF_CPF_CNPJ, F_REP_NOME, F_REP_CPF_CNPJ,
    F_TIPO_ESTADUAL, F_TIPO_TRABALHISTA, F_TIPO_PRECATORIO,
    F_CONTA_1, F_CONTA_2, F_CONTA_3,
    F_FORMA_AUTORIZACAO_PERMANENTE, F_FORMA_CONVENIO_DJC,
    F_FORMA_CREDITO_BENEFICIARIO, F_FORMA_CREDITO_REPRESENTANTE, F_FORMA_ESPECIE,
    F_BENEF_BANCO_NUM, F_BENEF_BANCO_NOME, F_BENEF_AGENCIA, F_BENEF_CONTA,
    F_BENEF_TITULAR_NOME, F_BENEF_TITULAR_CPF_CNPJ,
    F_BENEF_TIPO_CORRENTE, F_BENEF_TIPO_POUPANCA, F_BENEF_POUPANCA_VARIACAO,
    F_BENEF_VALOR_TOTAL, F_BENEF_VALOR_SALDO_REMANESCENTE,
    F_BENEF_VALOR_FIXO_CK, F_BENEF_VALOR_FIXO_RS,
    F_BENEF_VALOR_PARCIAL_CK, F_BENEF_VALOR_PARCIAL_RS,
    F_BENEF_VALOR_PERCENTUAL_CK, F_BENEF_VALOR_PERCENTUAL,
    F_REP_BANCO_NUM, F_REP_BANCO_NOME, F_REP_AGENCIA, F_REP_CONTA,
    F_REP_TITULAR_NOME, F_REP_TITULAR_CPF_CNPJ,
    F_REP_TIPO_CORRENTE, F_REP_TIPO_POUPANCA, F_REP_POUPANCA_VARIACAO,
    F_REP_VALOR_TOTAL, F_REP_VALOR_SALDO_REMANESCENTE,
    F_REP_VALOR_FIXO_CK, F_REP_VALOR_FIXO_RS,
    F_REP_VALOR_PARCIAL_CK, F_REP_VALOR_PARCIAL_RS,
    F_REP_VALOR_PERCENTUAL_CK, F_REP_VALOR_PERCENTUAL,
    F_ESPECIE_PREFIXO_AGENCIA,
    F_IR_ISENTO_SIM, F_IR_ISENTO_NAO,
    F_TEL_DDD, F_TEL_NUM, F_CEL_DDD, F_CEL_NUM, F_EMAIL,
    F_LOCAL, F_DATA_DIA, F_DATA_MES, F_DATA_ANO,
]:
    FIELD_PAGE[_name] = 1

for _name in [
    F_ANALFABETO_SIM, F_ANALFABETO_NAO,
    F_TESTEMUNHA1_NOME, F_TESTEMUNHA2_NOME, F_TESTEMUNHA1_CPF, F_TESTEMUNHA2_CPF,
    F_ROGO_SIGNER_NOME, F_ROGO_SIGNER_RG_NUM, F_ROGO_SIGNER_RG_ORGAO,
    F_ROGO_SIGNER_RG_DATA, F_ROGO_SIGNER_CPF,
    F_ROGO_BENEF_NOME, F_ROGO_BENEF_RG_NUM, F_ROGO_BENEF_RG_ORGAO,
    F_ROGO_BENEF_RG_DATA, F_ROGO_ALVARA_NUM,
    F_ROGO_SIGNER_PRINTED_NOME, F_ROGO_SIGNER_PRINTED_CPF,
    F_ROGO_TESTEMUNHA1_NOME, F_ROGO_TESTEMUNHA2_NOME,
    F_ROGO_TESTEMUNHA1_CPF, F_ROGO_TESTEMUNHA2_CPF,
]:
    FIELD_PAGE[_name] = 2

MESES_PT = {
    1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril", 5: "maio",
    6: "junho", 7: "julho", 8: "agosto", 9: "setembro", 10: "outubro",
    11: "novembro", 12: "dezembro",
}
