import os
import asyncio
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from aiqfome.database import Base, get_db
from aiqfome.main import app
from aiqfome.dependencies import get_current_client
from aiqfome.models import Client

# Carrega a URL do banco de dados de teste do .env
TEST_DATABASE_URL = os.getenv("DATABASE_URL_TEST")

engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)


# Fixture para criar e limpar as tabelas do banco de dados para cada teste
@pytest.fixture(scope="function", autouse=True)
async def db_setup_and_teardown():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Fixture que substitui a dependência get_db pela sessão de teste
@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


# Fixture que cria um cliente de teste para fazer requisições à API
@pytest.fixture(scope="function")
def test_client(db_session: AsyncSession) -> Generator[TestClient, None, None]:
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client

# Fixture para criar um usuário e obter um token de autenticação
@pytest.fixture(scope="function")
def auth_headers(test_client: TestClient) -> dict[str, str]:
    """Cria um usuário padrão e retorna os headers de autenticação."""
    test_client.post(
        "/clients/",
        json={"name": "Test User", "email": "test@example.com", "password": "password123"},
    )
    login_response = test_client.post(
        "/token",
        data={"username": "test@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}