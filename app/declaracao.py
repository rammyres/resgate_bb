"""
Geração da "Declaração de Isenção de Imposto de Renda" (depósito judicial /
precatório / RPV), conforme modelo da IN SRF nº 491, de 12/01/2005.

O conteúdo replica fielmente o texto da aba "Impressão" da planilha
declaracao.ods usada como referência: mesmo texto legal, mesma estrutura de
opções (isenção x Simples) e mesmo formato de valor por extenso.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from io import BytesIO

from num2words import num2words
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

from .field_map import MESES_PT


@dataclass
class DadosDeclaracao:
    nome: str
    cpf_cnpj: str
    endereco: str
    numero_processo: str
    vara: str
    municipio: str
    tipo: str  # "isento" ou "simples"
    local_assinatura: str  # local da assinatura (reaproveitado do "Local e Data" do formulário principal, não é o município do processo)
    valor: str | None = None  # string "14500.26" (ponto decimal)
    data: date | None = None


def valor_por_extenso(valor: float) -> str:
    """Converte um valor em reais para texto por extenso, ex.:
    14500.26 -> 'catorze mil e quinhentos reais e vinte e seis centavos'
    """
    texto = num2words(valor, lang="pt_BR", to="currency")
    return texto


def data_por_extenso(d: date) -> str:
    return f"{d.day} de {MESES_PT[d.month]} de {d.year}"


def formatar_valor_brl(valor: float) -> str:
    inteiro_str = f"{valor:,.2f}"
    # troca separadores: 14,500.26 -> 14.500,26
    inteiro_str = inteiro_str.replace(",", "X").replace(".", ",").replace("X", ".")
    return inteiro_str


def gerar_declaracao_pdf(dados: DadosDeclaracao) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm,
        leftMargin=2.5 * cm,
        rightMargin=2.5 * cm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TituloDecl", parent=styles["Heading2"], alignment=1, spaceAfter=2,
    )
    body_style = ParagraphStyle(
        "CorpoDecl", parent=styles["Normal"], fontSize=10.5, leading=15,
        spaceAfter=10, alignment=4,  # justified
    )
    small_style = ParagraphStyle(
        "PequenoDecl", parent=styles["Normal"], fontSize=9.5, leading=13,
        spaceAfter=10, alignment=4,
    )

    story = []
    story.append(Paragraph("DECLARAÇÃO DE ISENÇÃO", title_style))
    story.append(Paragraph("DEPÓSITO JUDICIAL", title_style))
    story.append(Paragraph("Precatório ou Requisição de Pequeno Valor", title_style))
    story.append(Paragraph("Pessoa Física ou Pessoa Jurídica", title_style))
    story.append(Spacer(1, 0.6 * cm))

    intro = (
        f"{dados.nome}, residente ou domiciliado(a) {dados.endereco}, "
        f"inscrito(a) no CPF/CNPJ sob o nº {dados.cpf_cnpj}, para fins da não "
        f"retenção do imposto de renda de que trata o art. 27 da lei nº "
        f"10.833 de 29 de dezembro de 2003, sobre rendimentos a serem "
        f"recebidos em cumprimento de decisão da Justiça Federal, conforme "
        f"Processo nº {dados.numero_processo} da(o) {dados.vara} de "
        f"{dados.municipio}, pagos pelo(a) Banco do Brasil, declara que:"
    )
    story.append(Paragraph(intro, body_style))

    marca_isento = "X" if dados.tipo == "isento" else "&nbsp;"
    marca_simples = "X" if dados.tipo == "simples" else "&nbsp;"

    if dados.tipo == "isento" and dados.valor is not None:
        valor_float = float(dados.valor)
        linha_isento = (
            f"( {marca_isento} ) o montante de R$ {formatar_valor_brl(valor_float)} "
            f"({valor_por_extenso(valor_float)}) - MAIS ACRÉSCIMOS – constitui "
            f"rendimento isento ou não tributável;"
        )
    else:
        linha_isento = (
            f"( {marca_isento} ) o montante de R$ "
            f"_______________________ (valor por extenso) - MAIS ACRÉSCIMOS - "
            f"constitui rendimento isento ou não tributável;"
        )
    story.append(Paragraph(linha_isento, body_style))

    linha_simples = (
        f"( {marca_simples} ) está inscrita no Sistema Integrado de Pagamento "
        f"de Impostos e Contribuições das Microempresas e das Empresas de "
        f"Pequeno Porte (Simples)."
    )
    story.append(Paragraph(linha_simples, body_style))

    aviso = (
        "O(a) beneficiário(a) fica ciente de que a falsidade na prestação "
        "destas informações o(a) sujeitará, juntamente com as demais "
        "pessoas que para ela concorrerem, às penalidades previstas na "
        "legislação tributária e penal, relativas à falsidade ideológica "
        "(art. 299 do Código Penal) e ao crime contra a ordem tributária "
        "(art. 1º da Lei nº 8.137, de 27 de dezembro de 1990)."
    )
    story.append(Paragraph(aviso, small_style))

    story.append(Spacer(1, 1 * cm))
    d = dados.data or date.today()
    local_data = f"{dados.local_assinatura}, {data_por_extenso(d)}"
    story.append(Paragraph(local_data, body_style))

    story.append(Spacer(1, 2 * cm))
    assinatura_style = ParagraphStyle(
        "Assinatura", parent=styles["Normal"], fontSize=10, alignment=1,
    )
    story.append(Paragraph("." * 53, assinatura_style))
    story.append(Paragraph(
        "Assinatura do(a) beneficiário(a) ou de seu representante legal",
        assinatura_style,
    ))
    story.append(Spacer(1, 1.4 * cm))
    story.append(Paragraph("." * 53, assinatura_style))
    story.append(Paragraph(
        "Abono da assinatura pela instituição financeira", assinatura_style,
    ))

    doc.build(story)
    return buf.getvalue()
