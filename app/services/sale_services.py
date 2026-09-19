from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.sale import Sale
from repository.sale_repository import sale_repository
from repository.product_repository import product_repository
from repository.user_repository import user_repository
from repository.customer_repository import customer_repository
from schemas.sale import SaleCreate, SaleUpdate


def generate_sale_number(db: Session) -> str:
    today_str = datetime.now().strftime("%Y%m%d")
    prefix = f"SALE-{today_str}-"

    count_today = (
        db.query(Sale)
        .filter(Sale.sale_number.like(f"{prefix}%"))
        .count()
    )
    next_number = count_today + 1
    return f"{prefix}{next_number:04d}"


def build_sale_item(db: Session, item_data: dict) -> dict:
    product = product_repository.get(db, item_data["product_id"])

    if not product or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {item_data['product_id']} not found or inactive",
        )

    quantity = item_data["quantity"]

    if product.quantity_in_stock < quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Insufficient stock for product '{product.name}'. "
                f"Available: {product.quantity_in_stock}, requested: {quantity}"
            ),
        )

    unit_price = product.unit_price         
    line_discount = item_data.get("line_discount") or 0
    line_total = (unit_price * quantity) - line_discount


    product.quantity_in_stock -= quantity

    return {
        "product_id": product.product_id,
        "quantity": quantity,
        "unit_price": unit_price,
        "line_discount": line_discount,
        "line_total": line_total,
    }


def validate_payments(payments_data: list[dict], total_amount) -> None:
    total_paid = sum(p["amount"] for p in payments_data)

    if total_paid != total_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Payment amounts ({total_paid}) do not match "
                f"sale total ({total_amount})"
            ),
        )


def get_sale(db: Session, id: int):
    sale = sale_repository.get(db, id)
    if not sale:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")
    return sale


def list_sales(db: Session):
    return sale_repository.get_all(db)


TAX_RATE = 0 


def create_sale(db: Session, data: SaleCreate):
    sale_data = data.model_dump()
    items_data = sale_data.pop("sale_items")
    payments_data = sale_data.pop("payments")
    if not user_repository.get(db, sale_data["user_id"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist")

    if sale_data.get("customer_id") is not None:
        if not customer_repository.get(db, sale_data["customer_id"]):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Customer does not exist")

    built_items = [build_sale_item(db, item) for item in items_data]
    

    subtotal = sum(item["line_total"] for item in built_items)
    discount_amount = sale_data.get("discount_amount") or 0
    tax_amount = subtotal * TAX_RATE
    total_amount = subtotal - discount_amount + tax_amount

    validate_payments(payments_data, total_amount)

    sale_number = generate_sale_number(db)

    sale = Sale(
        sale_number=sale_number,
        customer_id=sale_data.get("customer_id"),
        user_id=sale_data["user_id"],
        subtotal=subtotal,
        discount_amount=discount_amount,
        tax_amount=tax_amount,
        total_amount=total_amount,
        status="Completed",
    )
    db.add(sale)
    db.flush()
    
    from models.sale_item import SaleItem
    for item in built_items:
        db.add(SaleItem(sale_id=sale.sale_id, **item))

    from models.payment import Payment
    for payment in payments_data:
        db.add(Payment(
            sale_id=sale.sale_id,
            payment_method=payment["payment_method"],
            amount=payment["amount"],
            transaction_ref=payment.get("transaction_ref"),
            status="Approved",
        ))

    db.commit()
    db.refresh(sale)
    return sale


def update_sale(db: Session, sale_id: int, data: SaleUpdate):
    sale = get_sale(db, sale_id)
    return sale_repository.update(db, sale, data.model_dump(exclude_unset=True))


def delete_sale(db: Session, sale_id: int):
    sale = get_sale(db, sale_id)
    sale_repository.delete(db, sale)