FROM python:3.12-slim

# Evita .pyc e garante logs sem buffer (aparecem direto no `docker logs`)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependências primeiro (cache de layer melhor)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código (inclui app/pdf_assets/formulario.pdf)
COPY . .

# Usuário não-root
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5051

# Healthcheck usa a própria rota /healthz do projeto
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request,sys; urllib.request.urlopen('http://127.0.0.1:5051/healthz').read()" || exit 1

# gunicorn lendo o app factory via wsgi.py
CMD ["gunicorn", "--bind", "0.0.0.0:5051", "--workers", "2", "--timeout", "60", "wsgi:app"]