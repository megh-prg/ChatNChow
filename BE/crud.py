from sqlalchemy.orm import Session
from BE import models, schemas
from datetime import datetime
import random

# Custom exceptions
class OrderNotFoundError(Exception):
    pass

class PaymentNotFoundError(Exception):
    pass

class MenuItemNotFoundError(Exception):
    pass

# User operations
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    # In a real app, you'd hash the password
    hashed_password = user.password
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# crud.py
def get_order_details(db: Session, order_id: int):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        return None

    # Get customer info
    customer = db.query(models.User).filter(models.User.id == order.user_id).first()

    # Get order items
    items = []
    for item in order.order_items:
        menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == item.menu_item_id).first()
        items.append({
            "item_id": item.id,
            "name": menu_item.name if menu_item else "Unknown Item",
            "quantity": item.quantity,
            "price": float(item.price),
        })

    # Get delivery info (if exists)
    delivery_info = None
    if order.delivery:
        delivery_info = {
            "delivery_address": order.delivery.delivery_address if order.delivery else None,
            "delivery_date": order.delivery.delivery_date if order.delivery else None,
            "status": order.delivery.status if order.delivery else None
        }

    # Get payment info (if exists)
    payment_info = None
    if order.payment:
        payment_info = {
            "status": order.payment.status,
            "amount": float(order.payment.amount)
        }

    return {
        "order_id": order.id,
        "customer_username": customer.username if customer else "Unknown Customer",
        "created_at": order.created_at,
        "status": order.status,
        "items": items,
        "delivery": delivery_info,
        "payment": payment_info,
        "total": float(order.total) if order.total else 0.0,
        "restaurant": order.restaurant.name if order.restaurant else "Unknown Restaurant"
    }

# Restaurant operations
def get_restaurant(db: Session, restaurant_id: int):
    return db.query(models.Restaurant).filter(models.Restaurant.id == restaurant_id).first()


def get_menu_items_by_restaurant(db: Session, restaurant_id: int):
    return db.query(models.MenuItem).filter(models.MenuItem.restaurant_id == restaurant_id).all()

# Order operations
def create_order(db: Session, order: schemas.OrderCreate):
    # Calculate final total amount
    total_amount = 0.0
    order_items = []

    for item in order.items:
        menu_item = get_menu_item(db, item.menu_item_id)
        if not menu_item:
            raise MenuItemNotFoundError(f"Menu item with id {item.menu_item_id} not found")
        # Use the price from the request or from the database
        price = item.price if hasattr(item, 'price') and item.price else menu_item.price
        total_amount += float(price) * item.quantity
        order_items.append(models.OrderItem(
            menu_item_id=item.menu_item_id,
            quantity=item.quantity,
            price=price
        ))

    # Create the order
    db_order = models.Order(
        user_id=order.user_id,
        restaurant_id=order.restaurant_id,
        total=total_amount,
        status="pending"
    )

    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # Add order items with the correct order_id
    for item in order_items:
        item.order_id = db_order.id
        db.add(item)
    db.commit()

    return db_order

def get_order(db: Session, order_id: int):
    return db.query(models.Order).filter(models.Order.id == order_id).first()

def update_order(db: Session, order_id: int, order_update: schemas.OrderUpdate):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not db_order:
        raise OrderNotFoundError(f"Order with id {order_id} not found")

    # Update order fields
    if order_update.status is not None:
        db_order.status = order_update.status
    db.commit()
    db.refresh(db_order)
    return db_order

# Payment operations
def create_payment(db: Session, payment: schemas.PaymentCreate):
    db_payment = models.Payment(
        order_id=payment.order_id,
        amount=payment.amount,
        method=payment.method,
        transaction_id=payment.transaction_id,
        status='pending'
    )

    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    
    # After payment is created, update order status to 'confirmed'
    db_order = db.query(models.Order).filter(models.Order.id == payment.order_id).first()
    if db_order:
        db_order.status = 'confirmed'
        db.commit()
    
    return db_payment

def update_payment_status(db: Session, payment_id: int, status: str):
    db_payment = db.query(models.Payment).filter(models.Payment.id == payment_id).first()
    if not db_payment:
        raise PaymentNotFoundError(f"Payment with id {payment_id} not found")

    db_payment.status = status
    
    # If payment is completed, update order status
    if status == 'completed':
        db_order = db.query(models.Order).filter(models.Order.id == db_payment.order_id).first()
        if db_order:
            db_order.status = 'preparing'
            db.commit()
    
    db.commit()
    db.refresh(db_payment)
    return db_payment

# Utility functions
def get_order_items(db: Session, order_id: int):
    return db.query(models.OrderItem).filter(models.OrderItem.order_id == order_id).all()

def get_order_payment(db: Session, order_id: int):
    return db.query(models.Payment).filter(models.Payment.order_id == order_id).first()

def get_order_delivery(db: Session, order_id: int):
    return db.query(models.Delivery).filter(models.Delivery.order_id == order_id).first()




def get_restaurants(db: Session):
    return db.query(models.Restaurant).all()

def get_menu_items(db: Session, restaurant_id: int = None):
    query = db.query(models.MenuItem)
    if restaurant_id:
        query = query.filter(models.MenuItem.restaurant_id == restaurant_id)
    return query.all()

def get_menu_item(db: Session, item_id: int):
    return db.query(models.MenuItem).filter(models.MenuItem.id == item_id).first()