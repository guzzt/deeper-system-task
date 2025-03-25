FROM python:3.10-slim

WORKDIR /app

# Instalar dependências
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código do bot
COPY . .

CMD ["python", "telebot.py"]
