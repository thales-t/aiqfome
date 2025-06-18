import httpx
import asyncio
from typing import Optional, List, Dict

from .schemas import Product

FAKE_STORE_API_URL = "https://fakestoreapi.com/products"

async def get_product_by_id(product_id: int) -> Optional[Dict]:
    """Busca um único produto por ID na API externa."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{FAKE_STORE_API_URL}/{product_id}")
            response.raise_for_status()  # Lança exceção para status 4xx/5xx
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise e

async def get_products_details(product_ids: List[int]) -> List[Product]:
    """Busca detalhes de múltiplos produtos de forma concorrente."""
    async with httpx.AsyncClient() as client:
        tasks = [client.get(f"{FAKE_STORE_API_URL}/{pid}") for pid in product_ids]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

    products = []
    for res in responses:
        if isinstance(res, httpx.Response) and res.status_code == 200:
            products.append(Product.model_validate(res.json()))
        # Ignora erros (ex: produto não encontrado) para não quebrar a lista inteira
    
    return products