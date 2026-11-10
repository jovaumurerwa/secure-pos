from fastapi import Depends, FastAPI

from database import Base, engine
from dependencies import get_current_user
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
    auth as auth_router,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Secure POS API", version="1.1.0")

# Public: anyone can call these
app.include_router(auth_router.router)

# Protected: every route below needs a valid token (no token -> 401)
protected = [Depends(get_current_user)]

app.include_router(category_router.router, dependencies=protected)
app.include_router(supplier_router.router, dependencies=protected)
app.include_router(product_router.router, dependencies=protected)
app.include_router(user_router.router, dependencies=protected)
app.include_router(customer_router.router, dependencies=protected)
app.include_router(sale_router.router, dependencies=protected)
app.include_router(sale_item_router.router, dependencies=protected)
app.include_router(payment_router.router, dependencies=protected)
app.include_router(receipt_router.router, dependencies=protected)


@app.get("/")
def root():
    return {"message": "POS API is running"}