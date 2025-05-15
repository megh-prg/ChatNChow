from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import re
import json
from sqlalchemy.orm import Session
from BE import models, schemas, crud
from BE.database import SessionLocal, engine

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Food Delivery API", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Models
class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    order_id: Optional[int] = None

class ChatResponse(BaseModel):
    response: str
    detected_order_id: Optional[int] = None

# Helper Functions
def process_message(user_message: str, order_id: int = None, db: Session = None) -> str:
    """Process the user message and generate appropriate response."""
    message_lower = user_message.lower()
    
    # Handle different message patterns
    if any(keyword in message_lower for keyword in ["order food", "i want to order", "place an order"]):
        menu_items = crud.get_menu_items(db) if db else []
        menu_text = "\n".join([f"{item.id}. {item.name} - ${item.price:.2f}" for item in menu_items])
        return f"Great! Here's our menu:\n\n{menu_text}\n\nWhat would you like to order?"
    
    elif any(keyword in message_lower for keyword in ["manage order", "check status", "track order"]):
        if order_id:
            order = crud.get_order(db, order_id) if db else None
            return f"Order #{order_id} status: {order.status}" if order else "Order not found"
        return "Please provide your order ID to check status."

    elif user_message.startswith("#") or user_message.strip().isdigit():
        try:
            order_num = int(user_message.strip("#"))
            order = crud.get_order(db, order_num) if db else None
            return f"Order #{order_num} status: {order.status}" if order else "Order not found"
        except ValueError:
            return "Please provide a valid order number."

    return "I can help with orders or order status. How may I assist you?"
#add these below lines for the restro list to visble in the frontend
@app.get("/restaurants/", response_model=List[schemas.Restaurant])
def read_restaurants(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    restaurants = crud.get_restaurants(db, skip=skip, limit=limit)
    return restaurants

@app.get("/restaurants/{restaurant_id}", response_model=schemas.Restaurant)
def read_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    db_restaurant = crud.get_restaurant(db, restaurant_id=restaurant_id)
    if db_restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return db_restaurant

@app.get("/restaurants/{restaurant_id}/menu", response_model=List[schemas.MenuItem])
def read_menu_items(restaurant_id: int, db: Session = Depends(get_db)):
    menu_items = crud.get_menu_items_by_restaurant(db, restaurant_id=restaurant_id)
    if not menu_items:
        raise HTTPException(status_code=404, detail="No menu items found for this restaurant")
    return menu_items

# Routes
@app.get("/", status_code=status.HTTP_200_OK)
async def root() -> Dict[str, str]:
    return {"message": "Food Delivery API Service"}

@app.post("/chat", response_model=ChatResponse)
async def chat_with_bot(request: ChatRequest, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Handle chat messages with the food ordering bot."""
    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")
    
    user_message = request.messages[-1]
    response = process_message(user_message.content, request.order_id, db)
    
    # Detect order ID from response
    detected_order_id = request.order_id
    if "#" in response:
        if match := re.search(r'Order #(\d+)', response):
            detected_order_id = int(match.group(1))
    
    # Check for direct order number input
    if user_message.content.strip().startswith("#") or user_message.content.strip().isdigit():
        try:
            detected_order_id = int(user_message.content.strip().lstrip("#"))
        except ValueError:
            pass

    return {
        "response": str(response),
        "detected_order_id": detected_order_id
    }

@app.get("/orders/{order_id}", response_model=schemas.Order)
async def get_order(order_id: int, db: Session = Depends(get_db)) -> Any:
    """Get order details by ID."""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.post("/orders/create", response_model=schemas.Order)
async def create_order(
    order_data: schemas.OrderCreate, 
    db: Session = Depends(get_db)
) -> Any:
    """Create a new food order."""
    try:
        return crud.create_order(db, order_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create order")

# main.py
@app.get("/orders/{order_id}/details", response_model=schemas.OrderDetails)
def get_order_details(order_id: str, db: Session = Depends(get_db)):
    order_details = crud.get_order_details(db, order_id=order_id)
    if not order_details:
        raise HTTPException(status_code=404, detail="Order not found")
    return order_details

@app.get("/orders/{order_id}/status", response_model=Dict[str, str])
async def get_order_status(order_id: int, db: Session = Depends(get_db)) -> Dict[str, str]:
    """Get the status of an order."""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    payment_status = order.payment.status if order.payment else "not paid"
    return {"status": order.status, "payment_status": payment_status}

@app.put("/orders/{order_id}/update", response_model=schemas.Order)
async def update_order(
    order_id: int, 
    update_data: schemas.OrderUpdate, 
    db: Session = Depends(get_db)
) -> Any:
    """Update an existing order."""
    try:
        return crud.update_order(db, order_id, update_data)
    except crud.OrderNotFoundError:
        raise HTTPException(status_code=404, detail="Order not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update order")

@app.post("/payments/create", response_model=schemas.Payment)
async def create_payment(
    payment_data: schemas.PaymentCreate, 
    db: Session = Depends(get_db)
) -> Any:
    """Create a payment record."""
    try:
        return crud.create_payment(db, payment_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create payment")

@app.put("/payments/{payment_id}/status", response_model=schemas.Payment)
async def update_payment_status(
    payment_id: int, 
    status: str, 
    db: Session = Depends(get_db)
) -> Any:
    """Update payment status."""
    try:
        return crud.update_payment_status(db, payment_id, status)
    except crud.PaymentNotFoundError:
        raise HTTPException(status_code=404, detail="Payment not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update payment")
    
    
    #code fo main.py for 