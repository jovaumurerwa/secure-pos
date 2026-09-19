from fastapi import FastAPI

from database import Base, engine
from models import category, supplier, product, user, customer, sale, sale_item, payment, receipt

from routers import (
    category as category_router,
    supplier as supplier_router,
    product as product_router,
    user as user_router,
    customer as customer_router,
    sale as sale_router,
    sale_item as sale_item_router,
    payment as payment_router,
    receipt as receipt_router,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="POS API", version="1.0.0")

app.include_router(category_router.router)
app.include_router(supplier_router.router)
app.include_router(product_router.router)
app.include_router(user_router.router)
app.include_router(customer_router.router)
app.include_router(sale_router.router)
app.include_router(sale_item_router.router)
app.include_router(payment_router.router)
app.include_router(receipt_router.router)


@app.get("/")
def root():
    return {"message": "POS API is running"}