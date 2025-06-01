# Usar uma imagem Python oficial como imagem base
FROM python:3.11-slim

# Definir o diretório de trabalho no contentor
WORKDIR /app

# Copiar o ficheiro de requisitos primeiro para aproveitar o cache do Docker
COPY requirements.txt requirements.txt

# Instalar as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código da aplicação para o diretório de trabalho
COPY . .

# Expor a porta em que a aplicação Flask será executada
EXPOSE 5000

# Comando para executar a aplicação quando o contentor iniciar
# Usar 'flask run' com host 0.0.0.0 para torná-lo acessível externamente.
# As variáveis de ambiente FLASK_APP e FLASK_DEBUG (ou FLASK_ENV)
# definidas no docker-compose.yml serão usadas pelo comando 'flask run'.
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
