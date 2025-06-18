from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from . import crud, models, schemas, security
from .database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_client(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> models.Client:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    client = await crud.get_client_by_email(db, email=token_data.email)
    if client is None:
        raise credentials_exception
    return client