1. Documentação da API (Swagger/OpenAPI)<br>
<br>
Swagger UI: http://localhost:8000/docs<br>
ReDoc: http://localhost:8000/redoc<br>
<br>
<b>Endpoints Principais</b>:<br>
Autenticação<br>
    POST /token: Gera um token de acesso JWT para um cliente (login).
<br><br>
Clientes <br>
    POST /clients/: Cria um novo cliente (requer name, email, password).<br>
    GET /clients/logged/: Retorna os dados do cliente autenticado.<br>
    PUT /clients/logged/: Atualiza os dados (name ou email) do cliente autenticado.<br>
    DELETE /clients/logged/: Remove o cliente autenticado e todos os seus favoritos.<br>
<br>
Favoritos<br>
    POST /clients/logged/favorites/: Adiciona um produto à lista de favoritos do cliente autenticado. Requer o product_id.<br>
    GET /clients/logged/favorites/: Lista todos os produtos favoritos do cliente autenticado.<br>
    DELETE /clients/logged/favorites/{product_id}: Remove um produto da lista de favoritos do cliente autenticado.<br>
<br>
2. Como Rodar o Projeto<br>
Pré-requisitos:<br>
Docker e Docker Compose
<br><br>
Passos:<br>
Clone o Repositório:<br>
    git clone url-do-repositorio<br>
    cd aiqfome<br>
    <br>
    Configure as Variáveis de Ambiente:<br>
    Copie o arquivo de exemplo .env.example para um novo arquivo chamado .env <br>
    cp .env.example .env<br>
    O arquivo .env já contém valores padrão para rodar localmente.<br>
    <br>
    Inicie os Containers:<br>
    Use o Docker Compose para construir as imagens e iniciar os containers da aplicação e do banco de dados.<br>
    <br>
    docker-compose up --build<br>
    O servidor da API estará disponível em http://localhost:8000.
