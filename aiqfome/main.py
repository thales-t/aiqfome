from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.concurrency import asynccontextmanager
from aiqfome import models
from aiqfome.routers import auth, clientes, favoritos
from .database import engine
from aiqfome.schemas import Message

# Cria as tabelas no banco de dados na inicialização (para desenvolvimento)
# Em produção, use Alembic para migrações.
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        # await conn.run_sync(models.Base.metadata.drop_all) # Opcional: limpa tudo ao reiniciar
        await conn.run_sync(models.Base.metadata.create_all)
    yield

app = FastAPI(
    title="aiqfome - API de Favoritos",
    description="API para gerenciar clientes e seus produtos favoritos.",
    version="1.0.0",
    lifespan=lifespan
)


app.include_router(clientes.router)
app.include_router(favoritos.router)
app.include_router(auth.router)

@app.get('/', status_code=status.HTTP_200_OK, response_model=Message)
def read_root():
    return {'message': 'Olá Mundo!'}