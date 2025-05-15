from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import get_db
from . import models, schemas
from typing import Optional, Dict, List, Any
from pydantic import BaseModel
from .ai_service import (
    process_message, 
    handle_restaurant_selection, 
    handle_menu_item_selection,
    handle_checkout,
    get_order_status_response,
    handle_order_update
)

router = APIRouter(prefix="/chat", tags=["chat"])

class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    order_id: Optional[int] = None

class RestaurantSelectionRequest(BaseModel):
    restaurant_id: int

class MenuItemSelectionRequest(BaseModel):
    item_id: int
    quantity: int
    cart_items: List[Dict] = []

class CheckoutRequest(BaseModel):
    user_id: int
    restaurant_id: int
    cart_items: List[Dict]
    delivery_address: str
    payment_method: str  # "cash" or "card"

class OrderUpdateRequest(BaseModel):
    update_type: str  # "address", "instructions", "cancel"
    update_value: str

@router.post("/message")
async def chat_message(request: ChatRequest, db: Session = Depends(get_db)):
    """Process a chat message from the user"""
    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")
    
    user_message = request.messages[-1]
    if user_message.role != "user":
        raise HTTPException(status_code=400, detail="Last message must be from user")
    
    response = process_message(user_message.content, request.order_id, db)
    return response

@router.post("/select-restaurant")
async def select_restaurant(request: RestaurantSelectionRequest, db: Session = Depends(get_db)):
    """Handle restaurant selection"""
    return handle_restaurant_selection(request.restaurant_id, db)

@router.post("/select-menu-item")
async def select_menu_item(request: MenuItemSelectionRequest, db: Session = Depends(get_db)):
    """Handle menu item selection"""
    return handle_menu_item_selection(request.item_id, request.quantity, request.cart_items, db)

@router.post("/checkout")
async def checkout(request: CheckoutRequest, db: Session = Depends(get_db)):
    """Process checkout and create order"""
    return handle_checkout(
        request.user_id,
        request.restaurant_id,
        request.cart_items,
        request.delivery_address,
        request.payment_method,
        db
    )

@router.get("/order/{order_id}")
async def get_order_status(order_id: int, db: Session = Depends(get_db)):
    """Get order status and details"""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return get_order_status_response(order, db)

@router.post("/order/{order_id}/update")
async def update_order(order_id: int, request: OrderUpdateRequest, db: Session = Depends(get_db)):
    """Update an existing order"""
    return handle_order_update(order_id, request.update_type, request.update_value, db)