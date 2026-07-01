import json
from datetime import datetime
from io import BytesIO

from flask import Blueprint, render_template, request, jsonify, send_file
from pypdf import PdfReader, PdfWriter

from .build_payload import build_formulario_values
from .declaracao import gerar_declaracao_pdf
from .pdf_fill import fill_formulario
from .models import db, Solicitacao

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

    gerou_declaracao = declaracao_dados is not None
    if declaracao_dados is not None:
        declaracao_bytes = gerar_declaracao_pdf(declaracao_dados)
        declaracao_reader = PdfReader(BytesIO(declaracao_bytes))
        for page in declaracao_reader.pages:
            writer.add_page(page)

    output = BytesIO()
    writer.write(output)
    output.seek(0)

    try:
        registro = Solicitacao(
            quem_preencheu=payload.get("quem_preenche", ""),
            beneficiario_nome=(payload.get("beneficiario") or {}).get("nome", ""),
            tipo_deposito=payload.get("tipo_deposito", ""),
            forma_recebimento=payload.get("forma_recebimento", ""),
            gerou_declaracao_isencao=gerou_declaracao,
            beneficiario_analfabeto=(payload.get("analfabeto") or {}).get("resposta") == "sim",
            ip_origem=request.headers.get("X-Forwarded-For", request.remote_addr),
            payload_json=json.dumps(payload, ensure_ascii=False),
        )
        db.session.add(registro)
        db.session.commit()
    except Exception:
        db.session.rollback()
        # A geração do PDF não deve falhar por causa de um problema no
        # registro de auditoria; apenas seguimos sem persistir o registro.

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
