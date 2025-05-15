# BE/routers/orders.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import get_db
from . import models, schemas
from .schemas import OrderDetails 

router = APIRouter(
    prefix="/orders",
    tags=["orders"]
)

  # your DB models
 # your Pydantic schema
from database import get_db



@router.get("/orders/{order_id}", response_model=OrderDetails)
def get_order_details(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Construct and return full OrderDetails object
    return {
        "order_id": order.id,
        "customer_name": order.user.username,
        "order_time": order.order_time,
        "status": order.status,
        "delivery_address": order.delivery_address,
        "items": [],  # You can join OrderItems and fill this
        "delivery": None,  # Same for Delivery
        "payment": None,   # Same for Payment
        "total_amount": order.total_amount,
        "delivery_charge": order.delivery_charge,
        "tax": order.tax,
        "final_amount": order.final_amount,
        "special_instructions": order.special_instructions,
    }
@router.post("/", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    db_order = models.Order(**order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

@router.get("/{order_id}", response_model=schemas.Order)
def read_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order