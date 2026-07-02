"""
Preenchimento do formulario.pdf (AcroForm) a partir de um dicionário de
valores {field_id: valor}.

Observação importante sobre checkboxes
---------------------------------------
O formulário foi originalmente criado no LibreOffice e usa a fonte
"OpenSymbol" para desenhar o "check" dentro das caixas de seleção. O
pypdf, ao preencher o campo, atualiza corretamente o valor (/V) do
widget, mas em algumas versões não atualiza o estado de aparência (/AS) -
o atributo que diz qual XObject de aparência ("/Yes" ou "/Off") deve ser
desenhado. Sem isso, alguns visualizadores (e nosso próprio pipeline de
QA com poppler) mostram a caixa sempre vazia, mesmo com o valor certo
gravado no PDF.

Por isso, após chamar update_page_form_field_values, percorremos os
widgets de checkbox manualmente e forçamos /AS = valor escolhido. Isso
garante a marcação correta em qualquer leitor compatível com PDF
(Adobe Reader, Chrome, Edge, Foxit etc.), que foi o comportamento
validado durante o desenvolvimento desta ferramenta.
"""
from __future__ import annotations

from io import BytesIO
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject

from .field_map import ALL_CHECKBOX_FIELDS, FIELD_PAGE

BASE_PDF_PATH = Path(__file__).parent / "pdf_assets" / "formulario.pdf"


def fill_formulario(values: dict[str, str]) -> bytes:
    """Preenche o formulario.pdf com os valores informados.

    `values` é um dicionário {field_id: valor}. Para checkboxes, o valor
    deve ser '/Yes' ou '/Off' (ver field_map.CHECKED / field_map.UNCHECKED).
    Campos não mencionados permanecem com seu valor padrão (vazio /
    desmarcado).
    """
    reader = PdfReader(str(BASE_PDF_PATH))
    writer = PdfWriter(clone_from=reader)

    values_by_page: dict[int, dict[str, str]] = {}
    for field_id, value in values.items():
        page_num = FIELD_PAGE.get(field_id)
        if page_num is None:
            raise ValueError(f"Campo desconhecido no formulario.pdf: {field_id!r}")
        values_by_page.setdefault(page_num, {})[field_id] = value

    for page_num, page_values in values_by_page.items():
        writer.update_page_form_field_values(
            writer.pages[page_num - 1], page_values, auto_regenerate=False
        )

    # Corrige /AS nos widgets de checkbox para garantir renderização correta
    for page_num, page_values in values_by_page.items():
        page = writer.pages[page_num - 1]
        annots = page.get("/Annots")
        if not annots:
            continue
        for annot_ref in annots:
            widget = annot_ref.get_object()
            name = widget.get("/T")
            if name is None and widget.get("/Parent"):
                name = widget["/Parent"].get_object().get("/T")
            if name in page_values and name in ALL_CHECKBOX_FIELDS:
                widget[NameObject("/AS")] = NameObject(page_values[name])

    writer.set_need_appearances_writer(True)

    buf = BytesIO()
    writer.write(buf)
    return buf.getvalue()
