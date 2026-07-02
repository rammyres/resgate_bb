"""
Rotas Flask.

Importante: nenhum dado da solicitação (nome, CPF, dados bancários,
informações de IR etc.) é persistido no servidor. O PDF é gerado
inteiramente em memória a partir do payload recebido e devolvido
diretamente na resposta HTTP — nada é gravado em banco de dados ou disco.
"""
from datetime import datetime
from io import BytesIO

from flask import Blueprint, render_template, request, jsonify, send_file
from pypdf import PdfReader, PdfWriter

from .build_payload import build_formulario_values
from .declaracao import gerar_declaracao_pdf
from .pdf_fill import fill_formulario

bp = Blueprint("main", __name__)


@bp.get("/")
def index():
    return render_template("index.html")


@bp.post("/api/gerar-pdf")
def gerar_pdf():
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"erros": ["Requisição inválida (JSON ausente ou malformado)."]}), 400

    field_values, declaracao_dados, errors = build_formulario_values(payload)
    if errors:
        return jsonify({"erros": errors}), 422

    formulario_bytes = fill_formulario(field_values)
    reader = PdfReader(BytesIO(formulario_bytes))
    # Clonar (em vez de criar um PdfWriter vazio e usar add_page) é
    # essencial aqui: preserva o /AcroForm e a flag /NeedAppearances do
    # formulario.pdf preenchido, sem os quais os valores digitados nos
    # campos de texto deixam de ser exibidos pelos leitores de PDF.
    writer = PdfWriter(clone_from=reader)

    if declaracao_dados is not None:
        declaracao_bytes = gerar_declaracao_pdf(declaracao_dados)
        declaracao_reader = PdfReader(BytesIO(declaracao_bytes))
        for page in declaracao_reader.pages:
            writer.add_page(page)

    output = BytesIO()
    writer.write(output)
    output.seek(0)

    nome_beneficiario = (payload.get("beneficiario") or {}).get("nome", "formulario")
    nome_arquivo_safe = "".join(
        c for c in nome_beneficiario if c.isalnum() or c in " -_"
    ).strip().replace(" ", "_") or "formulario"
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"resgate_{nome_arquivo_safe}_{timestamp}.pdf"

    return send_file(
        output,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )


@bp.get("/healthz")
def healthz():
    return jsonify({"status": "ok"})
