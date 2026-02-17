from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from responses import ProductCreate, ProductResponse, close_db_pool, init_db_pool, get_all_db_products, get_product_by_id, create_product, delete_product, check_db_connection


app = FastAPI()

# We are using this because we dont want to hardcode the alb dns name in the frontend,
# and we want to be able to easily switch between development and production environments without changing the frontend code.
router = APIRouter(prefix="/api")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Should be after the CORS middleware so that it applies to all routes, including the health check.



@app.on_event("startup")
async def startup_event():
    await init_db_pool()

@app.on_event("shutdown")
async def shutdown_event():
    await close_db_pool()


@router.get("/health")
async def health_check():
    db_status = await check_db_connection()
    
    return {
        "status": "healthy" if db_status else "unhealthy",
        "database": "connected" if db_status else "disconnected"
    }

@router.get("/products", response_model=List[ProductResponse])
async def get_products():
    return await get_all_db_products()

@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    product = await get_product_by_id(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/products", response_model=ProductResponse)
async def create_new_product(product: ProductCreate):
    return await create_product(product)

@router.delete("/products/{product_id}", response_model=dict)
async def delete_product_by_id(product_id: int):
    success = await delete_product(product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

app.include_router(router)