from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from . import models, schemas, security

# --- CRUD para Clientes ---

async def get_client_by_email(db: AsyncSession, email: str) -> models.Client | None:
    result = await db.execute(select(models.Client).where(models.Client.email == email))
    return result.scalar_one_or_none()

async def create_client(db: AsyncSession, client: schemas.ClientCreate) -> models.Client:
    hashed_password = security.get_password_hash(client.password)
    db_client = models.Client(
        email=client.email, name=client.name, hashed_password=hashed_password
    )
    db.add(db_client)
    await db.commit()
    await db.refresh(db_client)
    return db_client

async def update_client(db: AsyncSession, client: models.Client, client_update: schemas.ClientUpdate) -> models.Client:
    update_data = client_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(client, key, value)
    
    await db.commit()
    await db.refresh(client)
    return client

async def delete_client(db: AsyncSession, client_id: int):
    client = await db.get(models.Client, client_id)
    if client:
        await db.delete(client)
        await db.commit()
    return client

# --- CRUD para Favoritos ---

async def get_favorite_product_ids_by_client(db: AsyncSession, client_id: int) -> list[int]:
    result = await db.execute(
        select(models.FavoriteProduct.product_id).where(models.FavoriteProduct.client_id == client_id)
    )
    return result.scalars().all()

async def is_product_in_favorites(db: AsyncSession, client_id: int, product_id: int) -> bool:
    result = await db.execute(
        select(models.FavoriteProduct).where(
            models.FavoriteProduct.client_id == client_id,
            models.FavoriteProduct.product_id == product_id
        )
    )
    return result.scalar_one_or_none() is not None

async def add_favorite(db: AsyncSession, client_id: int, product_id: int) -> models.FavoriteProduct | None:
    db_favorite = models.FavoriteProduct(client_id=client_id, product_id=product_id)
    db.add(db_favorite)
    try:
        await db.commit()
        await db.refresh(db_favorite)
        return db_favorite
    except IntegrityError: # Caso a constraint UNIQUE falhe
        await db.rollback()
        return None

async def remove_favorite(db: AsyncSession, client_id: int, product_id: int) -> models.FavoriteProduct | None:
    result = await db.execute(
        select(models.FavoriteProduct).where(
            models.FavoriteProduct.client_id == client_id,
            models.FavoriteProduct.product_id == product_id
        )
    )
    favorite_to_delete = result.scalar_one_or_none()
    
    if favorite_to_delete:
        await db.delete(favorite_to_delete)
        await db.commit()
    
    return favorite_to_delete