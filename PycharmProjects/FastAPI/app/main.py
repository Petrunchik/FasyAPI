from fastapi import FastAPI

from app.routers import category, products, auth, permission, reviews

app = FastAPI()

@app.get("/", tags=['main'])
async def welcome() -> dict:
    return {"Message": "my app"}


app.include_router(category.router)
app.include_router(products.router)
app.include_router(auth.router)
app.include_router(permission.router)
app.include_router(reviews.router)


