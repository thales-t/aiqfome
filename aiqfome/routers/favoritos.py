from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from aiqfome import crud, dependencies, fakestoreapi, models, schemas
from aiqfome.database import get_db
from typing import List


router = APIRouter(prefix='/clients/logged/favorites', tags=['Favorites'])

# --- Endpoints de Favoritos ---

@router.post("/", status_code=status.HTTP_201_CREATED, 
        summary="Adicionar Produto aos favoritos do cliente logado",   
        responses={
        status.HTTP_404_NOT_FOUND: {"description": "Produto não encontrado na API externa"},
        status.HTTP_409_CONFLICT: {"description": "Produto já existe na lista de favoritos"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Token de autenticação inválido ou ausente"},
    })
async def add_product_to_favorites(
    favorite: schemas.FavoriteProductCreate,
    db: AsyncSession = Depends(get_db),
    current_client: models.Client = Depends(dependencies.get_current_client)
):
    # 1. Validar se o produto existe na API externa
    product_data = await fakestoreapi.get_product_by_id(favorite.product_id)
    if not product_data:
        raise HTTPException(status_code=404, detail=f"Product with id {favorite.product_id} not found.")

    # 2. Verificar se já não está na lista de favoritos (evitar query duplicada)
    is_favorited = await crud.is_product_in_favorites(db, client_id=current_client.id, product_id=favorite.product_id)
    if is_favorited:
        raise HTTPException(status_code=409, detail="Product already in favorites.")

    # 3. Adicionar aos favoritos
    await crud.add_favorite(db=db, client_id=current_client.id, product_id=favorite.product_id)
    
    return {"message": "Product added to favorites successfully"}


@router.get("/", response_model=List[schemas.Product], summary="Lista dos produtos favoritos do usuário logado")
async def list_my_favorites(
    db: AsyncSession = Depends(get_db),
    current_client: models.Client = Depends(dependencies.get_current_client)
):
    favorite_ids = await crud.get_favorite_product_ids_by_client(db, client_id=current_client.id)
    if not favorite_ids:
        return []
    
    # Busca os detalhes completos dos produtos na API externa de forma concorrente
    products_details = await fakestoreapi.get_products_details(favorite_ids)
    return products_details


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remover Produto dos favoritos do cliente logado",  )
async def remove_product_from_favorites(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_client: models.Client = Depends(dependencies.get_current_client)
):
    favorite_removed = await crud.remove_favorite(db, client_id=current_client.id, product_id=product_id)
    if not favorite_removed:
        raise HTTPException(status_code=404, detail="Favorite product not found.")
    return