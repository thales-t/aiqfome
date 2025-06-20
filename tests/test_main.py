import pytest
from fastapi.testclient import TestClient

# Marca todos os testes neste arquivo para serem executados com asyncio
pytestmark = pytest.mark.asyncio

# --- Testes de Clientes e Autenticação ---

async def test_create_client_success(test_client: TestClient):
    response = await test_client.post(
        "/clients/",
        json={"name": "John Doe", "email": "john.doe@example.com", "password": "strongpassword"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "john.doe@example.com"
    assert "id" in data
    assert "hashed_password" not in data

async def test_create_client_duplicate_email(test_client: TestClient):
    # Cria o primeiro cliente
    await test_client.post(
        "/clients/",
        json={"name": "Jane Doe", "email": "jane.doe@example.com", "password": "password1"},
    )
    # Tenta criar o segundo com o mesmo e-mail
    response = await test_client.post(
        "/clients/",
        json={"name": "Jane Smith", "email": "jane.doe@example.com", "password": "password2"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

async def test_login_for_access_token(test_client: TestClient, auth_headers: dict):
    # A própria fixture 'auth_headers' já testa o login.
    # Aqui apenas validamos que o token foi recebido.
    assert "Authorization" in auth_headers
    assert "Bearer" in auth_headers["Authorization"]


# --- Testes de Favoritos ---

async def test_add_favorite_product_success(test_client: TestClient, auth_headers: dict, mocker):
    # Mock da API externa para simular um produto existente
    mocker.patch(
        "aiqfome.fakestoreapi.get_product_by_id",
        return_value={"id": 1, "title": "Test Product", "price": 10.0, "image": "url", "rating": {"rate": 4.5, "count": 120}},
    )

    response = await test_client.post(
        "/clients/logged/favorites/",
        json={"product_id": 1},
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json() == {"message": "Product added to favorites successfully"}

async def test_add_favorite_product_not_found(test_client: TestClient, auth_headers: dict, mocker):
    # Mock da API externa para simular um produto que não existe
    mocker.patch("aiqfome.fakestoreapi.get_product_by_id", return_value=None)
    
    response = await test_client.post(
        "/clients/logged/favorites/",
        json={"product_id": 999},
        headers=auth_headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Product with id 999 not found."

async def test_add_duplicate_favorite_product(test_client: TestClient, auth_headers: dict, mocker):
    mocker.patch(
        "aiqfome.fakestoreapi.get_product_by_id",
        return_value={"id": 2, "title": "Another Product"},
    )
    
    # Adiciona pela primeira vez
    await test_client.post("/clients/logged/favorites/", json={"product_id": 2}, headers=auth_headers)
    
    # Tenta adicionar novamente
    response = await test_client.post("/clients/logged/favorites/", json={"product_id": 2}, headers=auth_headers)
    
    assert response.status_code == 409
    assert response.json()["detail"] == "Product already in favorites."

async def test_list_favorites(test_client: TestClient, auth_headers: dict, mocker):
    # Adiciona um favorito primeiro
    mocker.patch(
        "aiqfome.fakestoreapi.get_product_by_id",
        return_value={"id":3,"title":"Fjallraven - Foldsack No. 1 Backpack, Fits 15 Laptops","price":109.95,
        "description":"Your perfect pack for everyday use and walks in the forest. Stash your laptop (up to 15 inches) in the padded sleeve, your everyday",
        "category":"men's clothing","image":"https://fakestoreapi.com/img/81fPKd-2AYL._AC_SL1500_.jpg","rating":{"rate":3.9,"count":120}},
    )
    await test_client.post("/clients/logged/favorites/", json={"product_id": 3}, headers=auth_headers)
    
    # Mock da chamada para listar os detalhes
    mock_product_details = [
       {"id":3,"title":"Fjallraven - Foldsack No. 1 Backpack, Fits 15 Laptops","price":109.95,
        "description":"Your perfect pack for everyday use and walks in the forest. Stash your laptop (up to 15 inches) in the padded sleeve, your everyday",
        "category":"men's clothing","image":"https://fakestoreapi.com/img/81fPKd-2AYL._AC_SL1500_.jpg","rating":{"rate":3.9,"count":120}}
    ]
    mocker.patch("aiqfome.fakestoreapi.get_products_details", return_value=mock_product_details)
    
    response = await test_client.get("/clients/logged/favorites/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == 3
    assert data[0]["title"] == "Fjallraven - Foldsack No. 1 Backpack, Fits 15 Laptops"

async def test_delete_favorite(test_client: TestClient, auth_headers: dict, mocker):
    # Adiciona um favorito
    mocker.patch("aiqfome.fakestoreapi.get_product_by_id", return_value={"id": 4})
    await test_client.post("/clients/logged/favorites/", json={"product_id": 4}, headers=auth_headers)
    
    # Deleta o favorito
    response = await test_client.delete("/clients/logged/favorites/4", headers=auth_headers)
    assert response.status_code == 204
    
    # Verifica que a lista de favoritos está vazia
    mocker.patch("aiqfome.fakestoreapi.get_products_details", return_value=[])
    list_response = await test_client.get("/clients/logged/favorites/", headers=auth_headers)
    assert list_response.json() == []

async def test_delete_non_existent_favorite(test_client: TestClient, auth_headers: dict):
    response = await test_client.delete("/clients/logged/favorites/999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Favorite product not found."