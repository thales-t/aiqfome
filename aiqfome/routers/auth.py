from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from aiqfome import crud, schemas, security
from aiqfome.database import get_db
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter()

# --- Endpoints de Autenticação ---
@router.post("/token", response_model=schemas.Token, tags=['Authentication'], summary="Obter Token de Acesso")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(get_db)
):
    """
    Autentica um cliente com e-mail e senha e retorna um token de acesso JWT.
    """
        
    client = await crud.get_client_by_email(db, email=form_data.username)
    if not client or not security.verify_password(form_data.password, client.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(data={"sub": client.email})
    return {"access_token": access_token, "token_type": "bearer"}
