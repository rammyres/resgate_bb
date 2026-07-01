from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Solicitacao(db.Model):
    """Registro de auditoria de cada PDF gerado.

    Guardamos o payload (JSON) que originou o documento e alguns campos
    soltos para facilitar buscas, mas NÃO armazenamos o PDF em si — ele é
    gerado sob demanda e devolvido diretamente ao navegador. Isso reduz a
    quantidade de dados sensíveis (CPF, dados bancários) persistidos no
    servidor.
    """

    __tablename__ = "solicitacoes"

    id = db.Column(db.Integer, primary_key=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    quem_preencheu = db.Column(db.String(20), nullable=False)
    beneficiario_nome = db.Column(db.String(200), nullable=False)
    tipo_deposito = db.Column(db.String(20), nullable=False)
    forma_recebimento = db.Column(db.String(30), nullable=False)
    gerou_declaracao_isencao = db.Column(db.Boolean, default=False)
    beneficiario_analfabeto = db.Column(db.Boolean, default=False)

    ip_origem = db.Column(db.String(64))

    # Payload completo, para fins de auditoria/reemissão. Como contém dados
    # pessoais (CPF, dados bancários), o acesso a esta tabela deve ser
    # restrito — veja recomendações de retenção no README.
    payload_json = db.Column(db.Text, nullable=False)

    def __repr__(self):  # pragma: no cover
        return f"<Solicitacao {self.id} {self.beneficiario_nome!r}>"
