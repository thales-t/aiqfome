# tests/conftest.py

import asyncio
from typing import AsyncGenerator, Generator
from contextlib import asynccontextmanager
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import ASGITransport, AsyncClient


# Importamos explicitamente os modelos para garantir que o SQLAlchemy (Base.metadata)
# saiba quais tabelas criar ANTES que a fixture 'db_setup_and_teardown' seja executada.
from aiqfome import models

from aiqfome.database import Base, get_db
from aiqfome.main import create_app 


# Definir a URL para o banco de dados SQLite em memória ---
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Criar o engine com configurações específicas para SQLite e testes ---
# O `connect_args` desabilita uma verificação de thread específica do SQLite.
# O `poolclass=StaticPool` garante que a mesma conexão seja usada em todos os momentos,
# o que é essencial para que o banco de dados em memória persista durante um teste.
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# A sessionmaker agora se vincula ao novo engine SQLite
TestAsyncSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

# Fixture para criar e limpar as tabelas do banco de dados para cada teste
@pytest.fixture(scope="function", name="db_setup_and_teardown")
async def db_setup_and_teardown():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all) # Create tables if needed
    async with TestAsyncSessionLocal() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all) # Clean up after tests

# # Fixture que substitui a dependência get_db pela sessão de teste em memória
# @pytest.fixture(scope="function")
# async def db_session() -> AsyncGenerator[AsyncSession, None]:
#     async with TestingSessionLocal() as session:
#         yield session


# Fixture do TestClient
@pytest.fixture(scope="function", name="test_client")
async def test_client(db_setup_and_teardown) -> Generator[TestClient, None, None]:
    
    # Cria a aplicação de teste sem o lifespan de produção
    app = create_app(lifespan=None)

    # Define a função de override.
    app.dependency_overrides[get_db] = lambda: db_setup_and_teardown # Override the database session dependency

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as client:
        yield client
    app.dependency_overrides = {} # Clear overrides after tests


# Fixture de autenticação
@pytest.fixture(scope="function")
async def auth_headers(test_client: TestClient) -> dict[str, str]:
    """Cria um usuário padrão e retorna os headers de autenticação."""
    await test_client.post(
        "/clients/",
        json={"name": "Test User", "email": "test@example.com", "password": "password123"},
    )
    login_response = await test_client.post(
        "/token",
        data={"username": "test@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}