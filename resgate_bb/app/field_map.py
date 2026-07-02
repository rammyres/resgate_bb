"""
Mapeamento dos campos do AcroForm do formulario.pdf (Banco do Brasil -
Solicitação de Resgate de Depósito Judicial / Precatório).

Este mapeamento foi construído analisando as posições (rects) de cada widget
no PDF original e cruzando com o texto das etiquetas na mesma região, e foi
validado visualmente preenchendo um conjunto de valores de teste e
renderizando o resultado.

Todas as caixas de seleção (checkboxes) usam '/Yes' para marcado e '/Off'
para desmarcado.
"""

# ---------------------------------------------------------------------------
# Página 1
# ---------------------------------------------------------------------------

# Identificação
F_BENEF_NOME = "TextBox1"
F_BENEF_CPF_CNPJ = "TextBox2"
F_REP_NOME = "TextBox3"
F_REP_CPF_CNPJ = "TextBox4"

# Tipo de depósito (checkboxes mutuamente exclusivos)
F_TIPO_ESTADUAL = "f"
F_TIPO_TRABALHISTA = "f1"
F_TIPO_PRECATORIO = "f2"

# Conta(s) judicial(ais) - até 3 campos
F_CONTA_1 = "TextBox5"
F_CONTA_2 = "TextBox51"
F_CONTA_3 = "TextBox52"

# Forma de recebimento (checkboxes mutuamente exclusivos)
F_FORMA_AUTORIZACAO_PERMANENTE = "f3"
F_FORMA_CONVENIO_DJC = "f4"
F_FORMA_CREDITO_BENEFICIARIO = "f19"
F_FORMA_CREDITO_REPRESENTANTE = "f12"
F_FORMA_ESPECIE = "f5"

# Bloco "Crédito em Conta BB ou TED para o BENEFICIÁRIO"
F_BENEF_BANCO_NUM = "TextBox6"
F_BENEF_BANCO_NOME = "TextBox7"
F_BENEF_AGENCIA = "TextBox82"
F_BENEF_CONTA = "TextBox92"
F_BENEF_TITULAR_NOME = "TextBox31"
F_BENEF_TITULAR_CPF_CNPJ = "TextBox10"
F_BENEF_TIPO_CORRENTE = "f16"
F_BENEF_TIPO_POUPANCA = "f18"
F_BENEF_POUPANCA_VARIACAO = "TextBox11"
F_BENEF_VALOR_TOTAL = "f17"
F_BENEF_VALOR_SALDO_REMANESCENTE = "f15"
F_BENEF_VALOR_FIXO_CK = "f13"
F_BENEF_VALOR_FIXO_RS = "TextBox14"
F_BENEF_VALOR_PARCIAL_CK = "f14"
F_BENEF_VALOR_PARCIAL_RS = "TextBox12"
F_BENEF_VALOR_PERCENTUAL = "TextBox13"

# Bloco "Crédito Conta BB ou TED para o REPRESENTANTE LEGAL"
F_REP_BANCO_NUM = "TextBox61"
F_REP_BANCO_NOME = "TextBox71"
F_REP_AGENCIA = "TextBox821"
F_REP_CONTA = "TextBox921"
F_REP_TITULAR_NOME = "TextBox311"
F_REP_TITULAR_CPF_CNPJ = "TextBox101"
F_REP_TIPO_CORRENTE = "f10"
F_REP_TIPO_POUPANCA = "f11"
F_REP_POUPANCA_VARIACAO = "TextBox111"
F_REP_VALOR_TOTAL = "f8"
F_REP_VALOR_SALDO_REMANESCENTE = "f9"
F_REP_VALOR_FIXO_CK = "f6"
F_REP_VALOR_FIXO_RS = "TextBox141"
F_REP_VALOR_PARCIAL_CK = "f7"
F_REP_VALOR_PARCIAL_RS = "TextBox121"
F_REP_VALOR_PERCENTUAL = "TextBox131"

# Pagamento em espécie
F_ESPECIE_PREFIXO_AGENCIA = "TextBox15"

# Imposto de renda
F_IR_ISENTO_SIM = "f52"
F_IR_ISENTO_NAO = "f51"

# Beneficiário analfabeto
F_ANALFABETO_SIM = "Caixa de sele#C3#A7#C3#A3o 1"
F_ANALFABETO_NAO = "Caixa de sele#C3#A7#C3#A3o 2"

# Contato
F_TEL_DDD = "Caixa de texto 1"
F_TEL_NUM = "Caixa de texto 2"
F_CEL_DDD = "Caixa de texto 3"
F_CEL_NUM = "Caixa de texto 4"
F_EMAIL = "Caixa de texto 5"

# Local e data
F_LOCAL = "Caixa de texto 6"
F_DATA_DIA = "Caixa de texto 7"
F_DATA_MES = "Caixa de texto 8"
F_DATA_ANO = "Caixa de texto 9"

# ---------------------------------------------------------------------------
# Página 2 - Beneficiário analfabeto / termo de quitação "a rogo"
# ---------------------------------------------------------------------------

# Quem assina a rogo do beneficiário analfabeto
F_ROGO_SIGNER_NOME = "TextBox211"
F_ROGO_SIGNER_RG_NUM = "TextBox231"
F_ROGO_SIGNER_RG_ORGAO = "TextBox232"
F_ROGO_SIGNER_RG_DATA = "TextBox201"
F_ROGO_SIGNER_CPF = "TextBox25"

# Dados do beneficiário analfabeto (a rogo de quem)
F_ROGO_BENEF_NOME = "TextBox110"
F_ROGO_BENEF_RG_NUM = "TextBox2311"
F_ROGO_BENEF_RG_ORGAO = "TextBox2312"
F_ROGO_BENEF_RG_DATA = "TextBox2313"
F_ROGO_ALVARA_NUM = "TextBox2314"

CHECKED = "/Yes"
UNCHECKED = "/Off"

ALL_CHECKBOX_FIELDS = {
    F_TIPO_ESTADUAL, F_TIPO_TRABALHISTA, F_TIPO_PRECATORIO,
    F_FORMA_AUTORIZACAO_PERMANENTE, F_FORMA_CONVENIO_DJC,
    F_FORMA_CREDITO_BENEFICIARIO, F_FORMA_CREDITO_REPRESENTANTE,
    F_FORMA_ESPECIE,
    F_BENEF_TIPO_CORRENTE, F_BENEF_TIPO_POUPANCA,
    F_BENEF_VALOR_TOTAL, F_BENEF_VALOR_SALDO_REMANESCENTE,
    F_BENEF_VALOR_FIXO_CK, F_BENEF_VALOR_PARCIAL_CK,
    F_REP_TIPO_CORRENTE, F_REP_TIPO_POUPANCA,
    F_REP_VALOR_TOTAL, F_REP_VALOR_SALDO_REMANESCENTE,
    F_REP_VALOR_FIXO_CK, F_REP_VALOR_PARCIAL_CK,
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
    F_BENEF_VALOR_PARCIAL_CK, F_BENEF_VALOR_PARCIAL_RS, F_BENEF_VALOR_PERCENTUAL,
    F_REP_BANCO_NUM, F_REP_BANCO_NOME, F_REP_AGENCIA, F_REP_CONTA,
    F_REP_TITULAR_NOME, F_REP_TITULAR_CPF_CNPJ,
    F_REP_TIPO_CORRENTE, F_REP_TIPO_POUPANCA, F_REP_POUPANCA_VARIACAO,
    F_REP_VALOR_TOTAL, F_REP_VALOR_SALDO_REMANESCENTE,
    F_REP_VALOR_FIXO_CK, F_REP_VALOR_FIXO_RS,
    F_REP_VALOR_PARCIAL_CK, F_REP_VALOR_PARCIAL_RS, F_REP_VALOR_PERCENTUAL,
    F_ESPECIE_PREFIXO_AGENCIA,
    F_IR_ISENTO_SIM, F_IR_ISENTO_NAO,
    F_ANALFABETO_SIM, F_ANALFABETO_NAO,
    F_TEL_DDD, F_TEL_NUM, F_CEL_DDD, F_CEL_NUM, F_EMAIL,
    F_LOCAL, F_DATA_DIA, F_DATA_MES, F_DATA_ANO,
]:
    FIELD_PAGE[_name] = 1

for _name in [
    F_ROGO_SIGNER_NOME, F_ROGO_SIGNER_RG_NUM, F_ROGO_SIGNER_RG_ORGAO,
    F_ROGO_SIGNER_RG_DATA, F_ROGO_SIGNER_CPF,
    F_ROGO_BENEF_NOME, F_ROGO_BENEF_RG_NUM, F_ROGO_BENEF_RG_ORGAO,
    F_ROGO_BENEF_RG_DATA, F_ROGO_ALVARA_NUM,
]:
    FIELD_PAGE[_name] = 2

MESES_PT = {
    1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril", 5: "maio",
    6: "junho", 7: "julho", 8: "agosto", 9: "setembro", 10: "outubro",
    11: "novembro", 12: "dezembro",
}
