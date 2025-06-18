1. Documentação da API (Swagger/OpenAPI)

Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc

Endpoints Principais
Autenticação
    POST /token: Gera um token de acesso JWT para um cliente (login).

Clientes
    POST /clients/: Cria um novo cliente (requer name, email, password).
    GET /clients/me/: Retorna os dados do cliente autenticado.
    PUT /clients/me/: Atualiza os dados (name ou email) do cliente autenticado.
    DELETE /clients/me/: Remove o cliente autenticado e todos os seus favoritos.

Favoritos
    POST /clients/me/favorites/: Adiciona um produto à lista de favoritos do cliente autenticado. Requer o product_id.
        Validação 1: A API verifica se o product_id existe na FakeStoreAPI antes de adicionar.
        Validação 2: A API impede a adição de um product_id duplicado para o mesmo cliente.
    GET /clients/me/favorites/: Lista todos os produtos favoritos do cliente autenticado. A API busca os IDs no banco de dados local e, em seguida, enriquece esses dados com as informações completas da FakeStoreAPI (título, imagem, preço).
    DELETE /clients/me/favorites/{product_id}: Remove um produto da lista de favoritos do cliente autenticado.

2. Como Rodar o Projeto
Pré-requisitos
Docker
Docker Compose

Passos
2.1 Clone o Repositório:

    git clone <url-do-repositorio>
    cd aiqfome
    
    Configure as Variáveis de Ambiente:
    Copie o arquivo de exemplo .env.example para um novo arquivo chamado .env.
    cp .env.example .env
    O arquivo .env já contém valores padrão para rodar localmente, mas você pode ajustar a SECRET_KEY se desejar.
    
    Inicie os Containers:
    Use o Docker Compose para construir as imagens e iniciar os containers da aplicação e do banco de dados.

    docker-compose up --build
    O servidor da API estará disponível em http://localhost:8000.