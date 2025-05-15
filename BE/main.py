from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import re
import logging
import qrcode
from io import BytesIO
from textblob import TextBlob
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import SessionLocal, engine

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="Food Delivery API", version="1.0.0")

# Track user sessions and states
user_sessions = {}

# Allow requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    order_id: Optional[int] = None
    user_id: Optional[str] = "default"  # Default user ID if not provided

class ChatResponse(BaseModel):
    response: str
    detected_order_id: Optional[int] = None
    order_data: Optional[Dict[str, Any]] = None
    state: Optional[str] = None

class PaymentStatusUpdate(BaseModel):
    status: str

def get_user_session(user_id: str) -> Dict:
    """Get or create a user session."""
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            "state": "default",
            "current_order_id": None,
            "last_restaurant_id": None,
            "last_menu_item_id": None
        }
    return user_sessions[user_id]

def update_user_session(user_id: str, **kwargs):
    """Update user session with new values."""
    session = get_user_session(user_id)
    session.update(kwargs)
    user_sessions[user_id] = session
    return session

def generate_qr_code(data: str) -> BytesIO:
    """Generate a QR code for payment."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_byte_array = BytesIO()
    img.save(img_byte_array, format="PNG")
    img_byte_array.seek(0)
    return img_byte_array

@app.get("/get_qr_code/{order_id}")
async def get_qr_code(order_id: int, db: Session = Depends(get_db)):
    """Get QR code for order payment."""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    payment = db.query(models.Payment).filter(models.Payment.order_id == order_id).first()
    if not payment or payment.status != "pending":
        raise HTTPException(status_code=400, detail="No pending payment for this order")
    
    qr_data = f"Payment for Order #{order_id}\nAmount: ${order.total:.2f}\nRestaurant: {order.restaurant.name}"
    qr_code = generate_qr_code(qr_data)
    return StreamingResponse(qr_code, media_type="image/png")

def generate_order_summary(order: models.Order, db: Session) -> str:
    try:
        restaurant = db.query(models.Restaurant).get(order.restaurant_id)
        restaurant_name = restaurant.name if restaurant else "Unknown Restaurant"
        
        # Get menu items for the order
        item_names = []
        for item in order.order_items:
            menu_item = db.query(models.MenuItem).get(item.menu_item_id)
            if menu_item:
                item_names.append(menu_item.name)
        
        if not item_names:
            return "Your order has been placed successfully!"
            
        total = float(order.total) if order.total else 0.0
        
        # Create a nice item list with proper grammar
        if len(item_names) == 1:
            item_list = item_names[0]
        else:
            item_list = ", ".join(item_names[:-1]) + f", and {item_names[-1]}"

        summary = (
            f"Got it! You've ordered {item_list} from {restaurant_name}. "
            f"That'll be ${total:.2f}. Expect it in 30–40 minutes. Bon appétit! 🍽️"
        )
        return summary

    except Exception as e:
        logger.error(f"Error in order summary: {e}")
        return "Your order has been placed successfully!"
    



@app.post("/chat")
async def chat_with_bot(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        logger.info(f"Received chat request: {request}")

        messages = request.messages
        if not messages:
            return {"response": "No messages provided."}

        user_message = messages[-1].content.strip()
        order_id = request.order_id
        user_id = request.user_id
        session = get_user_session(user_id)
        current_state = session["state"]

        logger.info(f"Processing message: {user_message}, order_id: {order_id}, state: {current_state}")

        # Handle cancel order flow
        if "cancel order" in user_message.lower() or current_state == "cancellation_flow":
            if current_state != "cancellation_flow":
                update_user_session(user_id, state="cancellation_flow")
                return {
                    "response": "Please enter your order ID to proceed with cancellation.",
                    "state": "cancellation_flow"
                }
            
            # User has entered order ID
            if user_message.isdigit():
                order_id = int(user_message)
                try:
                    # Use the cancel_order endpoint
                    response = await cancel_order(order_id, db)
                    
                    # Add refund timeline and agent support options
                    if "refund" in response["message"].lower():
                        response["message"] += "\n\nYour refund will be processed within 7 working days."
                    
                    response["message"] += "\n\nWould you like to:\n1. Talk to a real agent\n2. Place a new order\n3. Track another order"
                    update_user_session(user_id, state="post_cancellation")
                    return {"response": response["message"], "state": "post_cancellation"}
                except HTTPException as e:
                    return {
                        "response": f"{e.detail}\n\nWould you like to:\n1. Try another order ID\n2. Talk to a real agent\n3. Go back to main menu",
                        "state": "cancellation_flow"
                    }
            else:
                return {
                    "response": "Please enter a valid order ID (numbers only).",
                    "state": "cancellation_flow"
                }

        # Handle post-cancellation options
        if current_state == "post_cancellation":
            if user_message.lower() in ["1", "talk to agent", "agent"]:
                return {
                    "response": "Connecting you to a real agent. Please wait a moment...\n\nIn the meantime, you can:\n1. Place a new order\n2. Track another order",
                    "state": "default"
                }
            elif user_message.lower() in ["2", "new order", "place order"]:
                update_user_session(user_id, state="default")
                return {"response": "Let's place a new order! Type 'new order' to begin.", "state": "default"}
            elif user_message.lower() in ["3", "track", "track order"]:
                update_user_session(user_id, state="default")
                return {"response": "Please enter the order ID you'd like to track.", "state": "default"}

        # Add cancel order option to order confirmation
        if current_state == "order_confirmed":
            response = (
                f"Your order has been confirmed!\n"
                f"Order #{session['current_order_id']}\n"
                f"Total: ${order.total:.2f}\n\n"
                f"Would you like to:\n"
                f"1. Track this order\n"
                f"2. Cancel this order\n"
                f"3. Talk to a real agent"
            )
            update_user_session(user_id, state="post_order")
            return {"response": response, "state": "post_order"}

        # Handle post-order options
        if current_state == "post_order":
            if user_message.lower() in ["1", "track", "track order"]:
                return {"response": f"Tracking order #{session['current_order_id']}...", "state": "tracking"}
            elif user_message.lower() in ["2", "cancel", "cancel order"]:
                update_user_session(user_id, state="cancellation_flow")
                return {
                    "response": "Please confirm your order ID to proceed with cancellation.",
                    "state": "cancellation_flow"
                }
            elif user_message.lower() in ["3", "agent", "talk to agent"]:
                return {
                    "response": "Connecting you to a real agent. Please wait a moment...",
                    "state": "default"
                }

        # Reset state for new actions
        if any(kw in user_message.lower() for kw in ["new order", "track", "status", "where", "check", "manage"]):
            update_user_session(user_id, state="default")

        # Handle track order
        if any(kw in user_message.lower() for kw in ["track", "status", "where", "check"]):
            if order_id:
                order = crud.get_order(db, order_id)
                if order:
                    details = crud.get_order_details(db, order_id)
                    response = f"Order #{order_id} Status: {order.status}\nTotal: ${order.total:.2f}"
                    
                    if details and hasattr(details, 'order_items'):
                        response += "\nItems:\n"
                        for item in details.order_items:
                            menu_item = db.query(models.MenuItem).get(item.menu_item_id)
                            if menu_item:
                                response += f"- {menu_item.name}: ${item.price:.2f}\n"
                    
                    if details and hasattr(details, 'payment'):
                        response += f"\nPayment: {details.payment.status}"
                    
                    # Add next steps based on order status
                    if order.status == "pending" and (not details.payment or details.payment.status != "completed"):
                        response += "\n\nWould you like to:\n1. Pay Now\n2. Cancel Order"
                        update_user_session(user_id, state="managing_order", current_order_id=order_id)
                    else:
                        response += "\n\nWould you like to:\n1. Place New Order\n2. Track Another Order"
                        update_user_session(user_id, state="default")
                    
                    return {"response": response, "order_id": order_id, "state": session["state"]}
                return {"response": "Order not found. Please check your order ID."}
            else:
                return {"response": "Please enter your order ID to track your order."}

        # Handle new order
        if "new order" in user_message.lower():
            restaurants = db.query(models.Restaurant).all()
            if restaurants:
                response = "Choose a restaurant:\n" + "\n".join(f"{r.id}. {r.name} ({r.cuisine})" for r in restaurants)
                update_user_session(user_id, state="selecting_restaurant")
                return {"response": response, "state": "selecting_restaurant"}
            return {"response": "No restaurants available at the moment."}

        # Handle payment selection state
        if current_state == "awaiting_payment":
            if user_message.lower() in ["1", "pay now", "pay", "payment"]:
                if session["current_order_id"]:
                    order = crud.get_order(db, session["current_order_id"])
                    if order:
                        # Create payment record
                        payment_data = schemas.PaymentCreate(
                            order_id=session["current_order_id"],
                            amount=float(order.total),
                            method="online",
                            status="pending"
                        )
                        payment = crud.create_payment(db, payment_data)
                        
                        response = (
                            f"Please scan the QR code to complete your payment of ${order.total:.2f}.\n"
                            f"Order #{session['current_order_id']}\n"
                            f"Restaurant: {order.restaurant.name}\n\n"
                            f"QR Code URL: http://localhost:8000/get_qr_code/{session['current_order_id']}\n\n"
                            f"Would you like to:\n"
                            f"1. Cancel this order\n"
                            f"2. Track this order\n"
                            f"3. Talk to a real agent"
                        )
                        update_user_session(user_id, state="payment_initiated")
                        return {
                            "response": response,
                            "order_id": session["current_order_id"],
                            "qr_code_url": f"http://localhost:8000/get_qr_code/{session['current_order_id']}",
                            "state": "payment_initiated"
                        }
                return {"response": "Order not found. Please try placing a new order."}
            
            elif user_message.lower() in ["2", "cod", "cash on delivery"]:
                if session["current_order_id"]:
                    order = crud.get_order(db, session["current_order_id"])
                    if order:
                        # Create payment record for COD
                        payment_data = schemas.PaymentCreate(
                            order_id=session["current_order_id"],
                            amount=float(order.total),
                            method="cod",
                            status="pending"
                        )
                        payment = crud.create_payment(db, payment_data)
                        
                        response = (
                            f"Cash on Delivery selected for Order #{session['current_order_id']}.\n"
                            f"Total amount: ${order.total:.2f}\n"
                            f"Please have the exact amount ready when your order arrives."
                        )
                        update_user_session(user_id, state="order_confirmed")
                        return {
                            "response": response,
                            "order_id": session["current_order_id"],
                            "state": "order_confirmed"
                        }
                return {"response": "Order not found. Please try placing a new order."}
            
            else:
                return {
                    "response": "Please choose a valid payment method:\n1. Pay Now (Online Payment)\n2. Cash on Delivery (COD)",
                    "state": "awaiting_payment"
                }

        # Handle managing order state
        if current_state == "managing_order":
            if user_message.lower() in ["1", "pay now", "pay", "payment"]:
                if session["current_order_id"]:
                    order = crud.get_order(db, session["current_order_id"])
                    if order:
                        # Create payment record
                        payment_data = schemas.PaymentCreate(
                            order_id=session["current_order_id"],
                            amount=float(order.total),
                            method="online",
                            status="pending"
                        )
                        payment = crud.create_payment(db, payment_data)
                        
                        response = (
                            f"Please scan the QR code to complete your payment of ${order.total:.2f}.\n"
                            f"Order #{session['current_order_id']}\n"
                            f"Restaurant: {order.restaurant.name}\n\n"
                            f"QR Code URL: http://localhost:8000/get_qr_code/{session['current_order_id']}\n\n"
                            f"Would you like to:\n"
                            f"1. Cancel this order\n"
                            f"2. Track this order\n"
                            f"3. Talk to a real agent"
                        )
                        update_user_session(user_id, state="payment_initiated")
                        return {
                            "response": response,
                            "order_id": session["current_order_id"],
                            "qr_code_url": f"http://localhost:8000/get_qr_code/{session['current_order_id']}",
                            "state": "payment_initiated"
                        }
                return {"response": "Order not found. Please try placing a new order."}
            
            elif user_message.lower() in ["2", "cancel", "cancel order"]:
                if session["current_order_id"]:
                    try:
                        # Use the new cancel_order endpoint
                        response = await cancel_order(session["current_order_id"], db)
                        update_user_session(user_id, state="default")
                        return {"response": response["message"], "state": "default"}
                    except HTTPException as e:
                        return {"response": e.detail, "state": "managing_order"}
                return {"response": "Order not found. Please try placing a new order."}
            
            else:
                return {
                    "response": "Please choose a valid option:\n1. Pay Now\n2. Cancel Order",
                    "state": "managing_order"
                }

        # Handle payment initiated state
        if current_state == "payment_initiated":
            if user_message.lower() in ["1", "cancel", "cancel order"]:
                try:
                    response = await cancel_order(session["current_order_id"], db)
                    update_user_session(user_id, state="default")
                    return {"response": response["message"], "state": "default"}
                except HTTPException as e:
                    return {"response": e.detail, "state": "payment_initiated"}
            elif user_message.lower() in ["2", "track", "track order"]:
                return {"response": f"Tracking order #{session['current_order_id']}...", "state": "tracking"}
            elif user_message.lower() in ["3", "agent", "talk to agent"]:
                return {
                    "response": "Connecting you to a real agent. Please wait a moment...",
                    "state": "default"
                }
            else:
                return {
                    "response": "Please choose a valid option:\n1. Cancel this order\n2. Track this order\n3. Talk to a real agent",
                    "state": "payment_initiated"
                }

        # Handle numeric input - possible restaurant, menu item, or order ID
        if user_message.isdigit():
            user_number = int(user_message)

            # If last message was a restaurant menu prompt
            prev_msg = messages[-2].content.lower() if len(messages) > 1 else ""
            if "choose a restaurant" in prev_msg:
                restaurant = db.query(models.Restaurant).get(user_number)
                if restaurant:
                    menu = db.query(models.MenuItem).filter(models.MenuItem.restaurant_id == user_number).all()
                    if menu:
                        menu_text = f"Menu for {restaurant.name}:\n"
                        for item in menu:
                            menu_text += f"{item.id}. {item.name} - ${item.price:.2f}\n"
                            if item.description:
                                menu_text += f"   {item.description}\n"
                        menu_text += "\nEnter the number of the item you want to order."
                        update_user_session(user_id, state="selecting_menu_item", last_restaurant_id=user_number)
                        return {"response": menu_text, "state": "selecting_menu_item"}
                    return {"response": "No menu items available for this restaurant."}
                return {"response": "Invalid restaurant selection."}

            # If last message was a menu display
            elif "menu for" in prev_msg.lower():
                menu_item = db.query(models.MenuItem).get(user_number)
                if menu_item:
                    try:
                        # Create order item first
                        order_item = {
                            "menu_item_id": menu_item.id,
                            "quantity": 1,
                            "price": float(menu_item.price)
                        }
                        
                        # Create order data
                        order_data = {
                            "user_id": 1,
                            "restaurant_id": menu_item.restaurant_id,
                            "total_amount": float(menu_item.price),
                            "items": [order_item]
                        }
                        
                        # Convert to Pydantic model
                        order_create = schemas.OrderCreate(**order_data)
                        
                        # Create the order
                        new_order = crud.create_order(db, order_create)
                        
                        # Generate order summary
                        summary = generate_order_summary(new_order, db)
                        
                        response = (
                            f"Order created successfully!\nOrder #{new_order.id}\nTotal: ${new_order.total:.2f}\n\n"
                            f"{summary}\n\n"
                            f"Please choose your payment method:\n"
                            f"1. Pay Now (Online Payment)\n"
                            f"2. Cash on Delivery (COD)\n\n"
                            f"Type '1' for Pay Now or '2' for COD."
                        )
                        # Update session with new order and state
                        update_user_session(
                            user_id,
                            state="awaiting_payment",
                            current_order_id=new_order.id,
                            last_menu_item_id=menu_item.id
                        )
                        return {
                            "response": response,
                            "order_id": new_order.id,
                            "state": "awaiting_payment"
                        }
                    except Exception as e:
                        logger.error(f"Error creating order: {str(e)}")
                        logger.exception("Full traceback:")
                        return {"response": "Sorry, there was an error creating your order. Please try again."}
                return {"response": "Invalid menu item selection."}

            # Else assume it's an order ID
            order = crud.get_order(db, user_number)
            if order:
                details = crud.get_order_details(db, user_number)
                response = f"Order #{user_number} Status: {order.status}\nTotal: ${order.total:.2f}"
                
                if details and hasattr(details, 'order_items'):
                    response += "\nItems:\n"
                    for item in details.order_items:
                        menu_item = db.query(models.MenuItem).get(item.menu_item_id)
                        if menu_item:
                            response += f"- {menu_item.name}: ${item.price:.2f}\n"
                
                if details and hasattr(details, 'payment'):
                    response += f"\nPayment: {details.payment.status}"
                
                # Add next steps based on order status
                if order.status == "pending" and (not details.payment or details.payment.status != "completed"):
                    response += "\n\nWould you like to:\n1. Pay Now\n2. Cancel Order"
                    update_user_session(user_id, state="managing_order", current_order_id=user_number)
                else:
                    response += "\n\nWould you like to:\n1. Place New Order\n2. Track Another Order"
                    update_user_session(user_id, state="default")
                
                return {"response": response, "order_id": user_number, "state": session["state"]}
            return {"response": "Order not found. Please check your order ID."}

        # Default help response
        return {
            "response": "I can help you with:\n1. Track an order - type 'track order'\n2. Place a new order - type 'new order'\nWhat would you like to do?",
            "state": "default"
        }

    except Exception as e:
        logger.exception("Error in /chat endpoint")
        return {"response": "Something went wrong. Please try again later."}

@app.post("/cancel_order/{order_id}")
async def cancel_order(order_id: int, db: Session = Depends(get_db)):
    """Cancel an order and process refund if applicable."""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if order can be cancelled
    if order.status not in ["pending", "confirmed"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Order cannot be cancelled in its current status: {order.status}"
        )
    
    # Get payment information
    payment = crud.get_order_payment(db, order_id)
    
    # Update order status
    order.status = "cancelled"
    db.commit()
    
    # Process refund if payment was made
    refund_message = ""
    if payment and payment.status == "completed":
        # Here you would integrate with your payment gateway
        # For now, we'll just update the payment status
        payment.status = "refunded"
        db.commit()
        refund_message = f" A refund of ${order.total:.2f} has been processed."
    
    return {
        "message": f"Order #{order_id} has been cancelled successfully.{refund_message}",
        "refund_processed": bool(payment and payment.status == "refunded")
    }
