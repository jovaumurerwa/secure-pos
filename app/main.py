import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from dependencies import cashier_can
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

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Secure POS API", version="1.2.0")

frontend_origins = [o.strip() for o in os.getenv("FRONTEND_ORIGINS", "http://localhost:3000").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    return response


app.include_router(auth_router.router)

ADMIN_ONLY = [Depends(cashier_can())]
CASHIER_READ = [Depends(cashier_can("GET"))]
CASHIER_SELL = [Depends(cashier_can("GET", "POST"))]

app.include_router(user_router.router, dependencies=ADMIN_ONLY)
app.include_router(supplier_router.router, dependencies=ADMIN_ONLY)
app.include_router(category_router.router, dependencies=CASHIER_READ)
app.include_router(product_router.router, dependencies=CASHIER_READ)
app.include_router(customer_router.router, dependencies=CASHIER_SELL)
app.include_router(sale_router.router, dependencies=CASHIER_SELL)
app.include_router(sale_item_router.router, dependencies=CASHIER_SELL)
app.include_router(payment_router.router, dependencies=CASHIER_SELL)
app.include_router(receipt_router.router, dependencies=CASHIER_SELL)


@app.get("/")
def root():
    return {"message": "POS API is running"}
