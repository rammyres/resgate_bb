# Resgate BB — Gerador de Formulário de Resgate (Depósito Judicial / Precatório)

Ferramenta web que coleta os dados de uma solicitação de resgate de depósito
judicial/precatório e exporta o `formulario.pdf` do Banco do Brasil já
preenchido — incluindo, quando aplicável, a Declaração de Isenção de Imposto
de Renda (modelo IN SRF nº 491/2005) anexada ao final do PDF.

## Como funciona

1. O usuário preenche um formulário web em etapas (wizard) com campos
   condicionais:
   - Beneficiário preenche sozinho, ou procurador/representante legal
     preenche em nome dele (nesse caso os dados do representante também são
     coletados).
   - Forma de recebimento: crédito em conta do beneficiário, crédito em
     conta do representante legal, ou pagamento em espécie.
   - Se o tipo de depósito for **Precatório ou RPV Federal** e o
     beneficiário se declarar **isento de IR**, uma seção adicional coleta
     os dados da Declaração de Isenção (nome, CPF/CNPJ, endereço, processo,
     vara, município, valor, data).
2. Ao enviar, o backend:
   - Valida os dados recebidos (a validação client-side é só uma
     conveniência; o servidor nunca confia apenas nela).
   - Preenche os campos do AcroForm do `formulario.pdf` original (nome,
     CPF/CNPJ, contas, checkboxes de tipo de depósito/forma de
     recebimento/tipo de conta/valor, dados bancários, IR, analfabeto,
     contato, local e data).
   - Se necessário, gera a página da Declaração de Isenção de IR
     (reportlab), com o valor por extenso calculado automaticamente
     (`num2words`), e a anexa como última página do PDF final.
   - Registra um resumo da solicitação em SQLite para fins de auditoria
     (não armazena o PDF gerado, apenas o payload).
   - Devolve o PDF final para download no navegador.

## Estrutura do projeto

```
resgate_bb/
├── app/
│   ├── __init__.py         # app factory
│   ├── routes.py           # rotas Flask (/, /api/gerar-pdf, /healthz)
│   ├── field_map.py        # mapeamento dos campos do AcroForm do formulario.pdf
│   ├── pdf_fill.py         # preenchimento do formulario.pdf
│   ├── declaracao.py       # geração da Declaração de Isenção de IR (reportlab)
│   ├── build_payload.py    # validação + tradução do JSON do wizard -> campos do PDF
│   ├── models.py           # modelo SQLAlchemy (auditoria)
│   ├── pdf_assets/formulario.pdf   # PDF original do BB (não editar)
│   ├── templates/          # index.html + macro _macros.html
│   └── static/{css,js}/    # estilo e lógica do wizard
├── wsgi.py                 # entrypoint gunicorn
├── requirements.txt
├── instance/                # banco sqlite fica aqui (criado automaticamente)
└── deploy/
    └── resgate-bb.service   # unit systemd
```

## Deploy na instância Oracle Cloud (Ubuntu, padrão `/opt/`)

Este projeto segue o mesmo padrão de deploy usado no Raro Tracker e nos
demais projetos Flask: `Flask + SQLAlchemy + SQLite`, `gunicorn`, `systemd`,
rodando como usuário `ubuntu` em `/opt/`.

```bash
# 1. Copiar o projeto para a instância (ex: via git ou scp)
sudo mkdir -p /opt/resgate-bb
sudo chown ubuntu:ubuntu /opt/resgate-bb
# copie os arquivos deste projeto para /opt/resgate-bb

# 2. Criar o virtualenv e instalar dependências
cd /opt/resgate-bb
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

# 3. Ajustar a SECRET_KEY no unit file (deploy/resgate-bb.service)
#    e copiá-lo para o systemd
sudo cp deploy/resgate-bb.service /etc/systemd/system/resgate-bb.service
sudo systemctl daemon-reload
sudo systemctl enable --now resgate-bb

# 4. Verificar
sudo systemctl status resgate-bb
curl http://127.0.0.1:5051/healthz
```

Igual ao Raro Tracker, o gunicorn fica em `0.0.0.0:5051` (HTTP puro). Para
acesso externo, abra a porta 5051 na Security List/NSG da OCI, ou — melhor —
coloque um Nginx como reverse proxy na frente com HTTPS (recomendado, já
que este formulário trata dados sensíveis: CPF, dados bancários,
informações de IR).

### Nginx + HTTPS (recomendado)

Diferente do Raro Tracker (onde a ausência de HTTPS só derruba o web push),
aqui a falta de HTTPS expõe CPF, dados bancários e dados de IR em texto
claro na rede. Vale a pena configurar um Nginx com Let's Encrypt/Certbot na
frente do gunicorn antes de divulgar a URL:

```nginx
server {
    listen 80;
    server_name resgate.seudominio.com.br;
    location / {
        proxy_pass http://127.0.0.1:5051;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
depois `sudo certbot --nginx -d resgate.seudominio.com.br`.

## Dados sensíveis e retenção

A tabela `solicitacoes` (SQLite, `instance/resgate_bb.db`) guarda o payload
completo de cada geração (CPF, dados bancários, valores) para fins de
auditoria/reemissão. Como esses dados são sensíveis:

- Restrinja o acesso ao arquivo `.db` no servidor (permissões do usuário
  `ubuntu`, sem exposição via Nginx).
- Considere uma rotina periódica (systemd timer, como já usado no
  devolução-indevida-tracker) para expurgar registros antigos, ex.:
  `DELETE FROM solicitacoes WHERE criado_em < date('now','-90 days');`
- O PDF gerado **não** é salvo no servidor — existe só em memória durante a
  requisição e é devolvido direto ao navegador.

## Rodando localmente para testes

```bash
cd resgate_bb
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
FLASK_APP=wsgi.py ./venv/bin/flask run --host 0.0.0.0 --port 5051
```
Acesse http://localhost:5051

## Extensão futura possível

- Botão de "pré-visualizar" o PDF no navegador antes do download definitivo.
- Autopreenchimento dos dados do beneficiário a partir de um CPF já
  cadastrado (se este formulário for integrado a outro sistema seu, como o
  tracker de devolução indevida).
- Suporte a assinatura eletrônica antes do envio ao BB.
