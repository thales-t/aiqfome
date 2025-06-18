import pytest
from fastapi.testclient import TestClient

# Marca todos os testes neste arquivo para serem executados com asyncio
pytestmark = pytest.mark.asyncio

# --- Testes de Clientes e Autenticação ---

def test_create_client_success(test_client: TestClient):
    response = test_client.post(
        "/clients/",
        json={"name": "John Doe", "email": "john.doe@example.com", "password": "strongpassword"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "john.doe@example.com"
    assert "id" in data
    assert "hashed_password" not in data

def test_create_client_duplicate_email(test_client: TestClient):
    # Cria o primeiro cliente
    test_client.post(
        "/clients/",
        json={"name": "Jane Doe", "email": "jane.doe@example.com", "password": "password1"},
    )
    # Tenta criar o segundo com o mesmo e-mail
    response = test_client.post(
        "/clients/",
        json={"name": "Jane Smith", "email": "jane.doe@example.com", "password": "password2"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_login_for_access_token(test_client: TestClient, auth_headers: dict):
    # A própria fixture 'auth_headers' já testa o login.
    # Aqui apenas validamos que o token foi recebido.
    assert "Authorization" in auth_headers
    assert "Bearer" in auth_headers["Authorization"]

def test_read_client_me(test_client: TestClient, auth_headers: dict):
    response = test_client.get("/clients/me/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"

def test_read_client_me_unauthorized(test_client: TestClient):
    response = test_client.get("/clients/me/")
    assert response.status_code == 401


# --- Testes de Favoritos ---

def test_add_favorite_product_success(test_client: TestClient, auth_headers: dict, mocker):
    # Mock da API externa para simular um produto existente
    mocker.patch(
        "app.fakestoreapi.get_product_by_id",
        return_value={"id": 1, "title": "Test Product", "price": 10.0, "image": "url", "rating": {"rate": 4.5, "count": 120}},
    )

    response = test_client.post(
        "/clients/me/favorites/",
        json={"product_id": 1},
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json() == {"message": "Product added to favorites successfully"}

def test_add_favorite_product_not_found(test_client: TestClient, auth_headers: dict, mocker):
    # Mock da API externa para simular um produto que não existe
    mocker.patch("app.fakestoreapi.get_product_by_id", return_value=None)
    
    response = test_client.post(
        "/clients/me/favorites/",
        json={"product_id": 999},
        headers=auth_headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Product with id 999 not found."

def test_add_duplicate_favorite_product(test_client: TestClient, auth_headers: dict, mocker):
    mocker.patch(
        "app.fakestoreapi.get_product_by_id",
        return_value={"id": 2, "title": "Another Product"},
    )
    
    # Adiciona pela primeira vez
    test_client.post("/clients/me/favorites/", json={"product_id": 2}, headers=auth_headers)
    
    # Tenta adicionar novamente
    response = test_client.post("/clients/me/favorites/", json={"product_id": 2}, headers=auth_headers)
    
    assert response.status_code == 409
    assert response.json()["detail"] == "Product already in favorites."

def test_list_favorites(test_client: TestClient, auth_headers: dict, mocker):
    # Adiciona um favorito primeiro
    mocker.patch(
        "app.fakestoreapi.get_product_by_id",
        return_value={"id": 3, "title": "A Great Product"},
    )
    test_client.post("/clients/me/favorites/", json={"product_id": 3}, headers=auth_headers)
    
    # Mock da chamada para listar os detalhes
    mock_product_details = [
        {"id": 3, "title": "A Great Product", "price": 99.9, "image": "url", "rating": {"rate": 5, "count": 1}}
    ]
    mocker.patch("app.fakestoreapi.get_products_details", return_value=mock_product_details)
    
    response = test_client.get("/clients/me/favorites/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == 3
    assert data[0]["title"] == "A Great Product"

def test_delete_favorite(test_client: TestClient, auth_headers: dict, mocker):
    # Adiciona um favorito
    mocker.patch("app.fakestoreapi.get_product_by_id", return_value={"id": 4})
    test_client.post("/clients/me/favorites/", json={"product_id": 4}, headers=auth_headers)
    
    # Deleta o favorito
    response = test_client.delete("/clients/me/favorites/4", headers=auth_headers)
    assert response.status_code == 204
    
    # Verifica que a lista de favoritos está vazia
    mocker.patch("app.fakestoreapi.get_products_details", return_value=[])
    list_response = test_client.get("/clients/me/favorites/", headers=auth_headers)
    assert list_response.json() == []

def test_delete_non_existent_favorite(test_client: TestClient, auth_headers: dict):
    response = test_client.delete("/clients/me/favorites/999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Favorite product not found."