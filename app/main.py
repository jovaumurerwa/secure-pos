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

# ---------- CORS: only our own frontend may call the API from a browser ----------
frontend_origins = [o.strip() for o in os.getenv("FRONTEND_ORIGINS", "http://localhost:3000").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,          # never "*" when sending credentials
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


# ---------- Security headers on every response ----------
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"   # browser must not guess file types
    response.headers["X-Frame-Options"] = "DENY"             # page can't be put inside another site (clickjacking)
    response.headers["Referrer-Policy"] = "no-referrer"      # don't leak URLs to other sites
    response.headers["Cache-Control"] = "no-store"           # don't cache sales or user data
    return response


# ---------- Routes ----------
# Public
app.include_router(auth_router.router)

# Who can do what (Admin can always do everything):
ADMIN_ONLY = [Depends(cashier_can())]                         # cashiers: nothing
CASHIER_READ = [Depends(cashier_can("GET"))]                  # cashiers: look only
CASHIER_SELL = [Depends(cashier_can("GET", "POST"))]          # cashiers: look + create, no edit/delete

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
