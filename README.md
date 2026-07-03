# Resgate BB — Gerador de Formulário de Resgate (Depósito Judicial / Precatório)

## (README.md e comentários do código gerados por IA)

Ferramenta web que coleta os dados de uma solicitação de resgate de depósito
judicial/precatório e exporta o `formulario.pdf` do Banco do Brasil já
preenchido — incluindo, quando aplicável, a Declaração de Isenção de Imposto
de Renda (modelo IN SRF nº 491/2005) anexada ao final do PDF.

## Como funciona

1. O usuário preenche um formulário web em etapas (wizard) com campos
   condicionais:

   - Beneficiário preenche sozinho, ou procurador/representante legal
     preenche em nome dele. Independentemente de quem preenche, há uma
     pergunta própria — "há um representante legal/procurador envolvido
     nesta solicitação?" — que libera os dados do representante e as
     opções de crédito para a conta dele, inclusive quando é o próprio
     beneficiário quem está preenchendo o formulário (ex.: para dividir o
     valor com o procurador).
   - Forma de recebimento: crédito em conta do beneficiário, crédito em
     conta do representante legal, divisão do valor entre as duas contas
     (usando as opções "Parcial R$/%" já previstas em cada bloco do PDF
     original), ou pagamento em espécie.
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
   - Devolve o PDF final para download no navegador.

Nenhum dado da solicitação é persistido no servidor: o PDF é montado
inteiramente em memória a partir do payload recebido e devolvido direto na
resposta HTTP. Não há banco de dados nem log de conteúdo dos formulários.

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
│   ├── pdf_assets/formulario.pdf   # PDF original do BB (não editar)
│   ├── templates/          # index.html + macro _macros.html
│   └── static/
│       ├── css/style.css
│       └── js/
│           ├── main.js     # wizard: campos condicionais, máscaras, combobox de bancos, envio
│           └── bancos.js   # lista de bancos (código + nome) para o combobox
├── wsgi.py                 # entrypoint gunicorn
├── requirements.txt
└── deploy/
    └── resgate-bb.service   # unit systemd
```

## Deploy na instância Oracle Cloud (Ubuntu, padrão `/opt/`)

Este projeto segue o mesmo padrão de deploy usado nos demais projetos
Flask: `Flask + gunicorn + systemd`, rodando como usuário `ubuntu` em
`/opt/`, na porta **5051** (distinta das demais: 3000, 5000, 5050 já estão
em uso por outros projetos).

### 1. Copiar o projeto e instalar dependências

```bash
sudo mkdir -p /opt/resgate-bb
sudo chown ubuntu:ubuntu /opt/resgate-bb
# copie os arquivos deste projeto para /opt/resgate-bb

cd /opt/resgate-bb
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

### 2. Gerar a SECRET_KEY

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Cole o resultado no lugar de `TROQUE_ESTA_CHAVE_EM_PRODUCAO` em
`deploy/resgate-bb.service`.

### 3. Instalar o serviço systemd

```bash
sudo cp deploy/resgate-bb.service /etc/systemd/system/resgate-bb.service
sudo systemctl daemon-reload
sudo systemctl enable --now resgate-bb
sudo systemctl status resgate-bb
curl http://127.0.0.1:5051/healthz
```

## Rodando localmente para testes

```bash
cd resgate_bb
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
FLASK_APP=wsgi.py ./venv/bin/flask run --host 0.0.0.0 --port 5051
```

Acesse http://localhost:5051

## TODO

- **Preenchimento automático via ID Depósito / SISBAJUD**: está sendo
  avaliada a viabilidade de um scraping do site do Banco do Brasil para,
  a partir do ID Depósito (SISBAJUD), recuperar automaticamente os dados
  do depósito judicial e pré-preencher o wizard.
- **Coleta automática de dados processuais via API pública do PJe**: está
  sendo avaliada a integração com a API pública do PJe para, a partir do
  número do processo (padrão CNJ), preencher automaticamente campos como
  vara/seção judiciária, município e partes do processo.
- **Atualização da versão do formulário de resgate**

 
