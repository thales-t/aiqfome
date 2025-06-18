from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from aiqfome import crud, dependencies, models, schemas
from aiqfome.database import get_db


router = APIRouter(prefix='/clients', tags=['clients'])

# --- Endpoints de Clientes ---

@router.post("/", response_model=schemas.Client, status_code=status.HTTP_201_CREATED, summary="Criar um novo cliente")
async def create_client(client: schemas.ClientCreate, db: AsyncSession = Depends(get_db)):
    db_client = await crud.get_client_by_email(db, email=client.email)
    if db_client:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await crud.create_client(db=db, client=client)

@router.get("/me", response_model=schemas.Client, summary="Obter dados do cliente autenticado")
async def read_client_me(current_client: models.Client = Depends(dependencies.get_current_client)):
    return current_client

@router.put("/me", response_model=schemas.Client, summary="Atualizar dados do cliente autenticado")
async def update_client_me(
    client_update: schemas.ClientUpdate,
    db: AsyncSession = Depends(get_db),
    current_client: models.Client = Depends(dependencies.get_current_client)
):
    # Verifica se o novo e-mail já está em uso por outro cliente
    if client_update.email and client_update.email != current_client.email:
        existing_client = await crud.get_client_by_email(db, email=client_update.email)
        if existing_client:
            raise HTTPException(status_code=400, detail="This email is already in use.")

    return await crud.update_client(db, current_client, client_update)

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT, summary="deletar cliente")
async def delete_client_me(
    db: AsyncSession = Depends(get_db),
    current_client: models.Client = Depends(dependencies.get_current_client)
):
    await crud.delete_client(db, client_id=current_client.id)
    return