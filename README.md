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
    GET /clients/me/: Retorna os dados do cliente autenticado.<br>
    PUT /clients/me/: Atualiza os dados (name ou email) do cliente autenticado.<br>
    DELETE /clients/me/: Remove o cliente autenticado e todos os seus favoritos.<br>
<br>
Favoritos<br>
    POST /clients/me/favorites/: Adiciona um produto à lista de favoritos do cliente autenticado. Requer o product_id.<br>
        Validação 1: A API verifica se o product_id existe na FakeStoreAPI antes de adicionar.<br>
        Validação 2: A API impede a adição de um product_id duplicado para o mesmo cliente.<br>
    GET /clients/me/favorites/: Lista todos os produtos favoritos do cliente autenticado. A API busca os IDs no banco de dados local e, em seguida, enriquece esses dados com as informações completas da FakeStoreAPI (título, imagem, preço).<br>
    DELETE /clients/me/favorites/{product_id}: Remove um produto da lista de favoritos do cliente autenticado.<br>
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
