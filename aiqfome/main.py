from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.concurrency import asynccontextmanager
from aiqfome import models
from aiqfome.routers import auth, clientes, favoritos
from .database import engine
from aiqfome.schemas import Message

# Cria as tabelas no banco de dados na inicialização (para desenvolvimento)
@asynccontextmanager
async def production_lifespan(app: FastAPI):
    async with engine.begin() as conn:
        # await conn.run_sync(models.Base.metadata.drop_all) # Opcional: limpa tudo ao reiniciar
        await conn.run_sync(models.Base.metadata.create_all)
    yield

# --- A FÁBRICA DE APLICAÇÃO ---
def create_app(lifespan=production_lifespan) -> FastAPI:
    """
    Cria e configura uma instância da aplicação FastAPI.
    """
    app = FastAPI(
        title="API de Favoritos - aiqfome",
        description="API para gerenciar clientes e seus produtos favoritos.",
        version="1.0.0",
        lifespan=lifespan  # Usa o lifespan que for passado (ou o de produção como padrão)
    )

    # Inclui os roteadores
    app.include_router(clientes.router)
    app.include_router(favoritos.router)
    app.include_router(auth.router)

    return app

app = create_app()

@app.get('/', status_code=status.HTTP_200_OK, response_model=Message)
def read_root():
    return {'message': 'Olá Mundo!'}