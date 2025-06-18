FROM python:3.13-slim
ENV POETRY_VIRTUALENVS_CREATE=false

# Define o diretório de trabalho dentro do container.
WORKDIR /app

# Copiar o código-fonte da nossa aplicação para o diretório de trabalho no container.
COPY . .

#instala o Poetry, nosso gerenciador de pacotes.
RUN pip install poetry

# Instalar dependências
RUN poetry config installer.max-workers 10
RUN poetry install --no-interaction --no-ansi --without dev



#  Execução
EXPOSE 8000

CMD poetry run uvicorn --host 0.0.0.0 aiqfome.main:app