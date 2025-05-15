from typing import Optional, List, Dict, Any
from . import crud, schemas, models
from sqlalchemy.orm import Session

def process_message(message: str, order_id: Optional[int], db: Session):
    message = message.lower().strip()
    
    # No current order context
    if not order_id:
        if "order food" in message or "place order" in message or "new order" in message:
            # Get restaurants to suggest
            restaurants = crud.get_restaurants(db, limit=10)
            return {
                "type": "restaurant_selection",
                "content": "Great! Let's start a new order. Please select a restaurant:",
                "restaurants": [
                    {
                        "id": r.id,
                        "name": r.name,
                        "address": r.address,
                        "image_url": r.image_url
                    } for r in restaurants
                ]
            }
        elif "manage order" in message or "check order" in message or "track order" in message:
            return {
                "type": "order_lookup",
                "content": "Please provide your order ID to check your order status."
            }
        else:
            return {
                "type": "welcome",
                "content": "Welcome to our Food Delivery Service! How can I help you today?",
                "options": [
                    {"text": "Order Food", "value": "order_food"},
                    {"text": "Manage Order", "value": "manage_order"}
                ]
            }
    else:
        # Handle order-specific commands
        order = crud.get_order(db, order_id)
        if not order:
            return {"type": "error", "content": "Order not found. Please check your order ID."}
        
        if "status" in message:
            return get_order_status_response(order, db)
        elif "update" in message or "change" in message:
            return {
                "type": "update_options",
                "content": "What would you like to update?",
                "options": [
                    {"text": "Delivery Address", "value": "address"},
                    {"text": "Special Instructions", "value": "instructions"},
                    {"text": "Cancel Order", "value": "cancel"}
                ]
            }
        else:
            return get_order_status_response(order, db)

def handle_restaurant_selection(restaurant_id: int, db: Session):
    """Handle when a user selects a restaurant"""
    restaurant = crud.get_restaurant(db, restaurant_id)
    if not restaurant:
        return {"type": "error", "content": "Restaurant not found. Please select another restaurant."}
    
    # Get menu items for the selected restaurant
    menu_items = crud.get_menu_items_by_restaurant(db, restaurant_id)
    
    # Group menu items by category
    categorized_menu = {}
    for item in menu_items:
        if item.category not in categorized_menu:
            categorized_menu[item.category] = []
        categorized_menu[item.category].append({
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "price": float(item.price),
            "image_url": item.image_url
        })
    
    return {
        "type": "menu_display",
        "restaurant": {
            "id": restaurant.id,
            "name": restaurant.name,
        },
        "categories": [
            {
                "name": category,
                "items": items
            } for category, items in categorized_menu.items()
        ]
    }

def handle_menu_item_selection(item_id: int, quantity: int, cart_items: List[Dict], db: Session):
    """Handle when a user adds an item to their cart"""
    menu_item = crud.get_menu_item(db, item_id)
    if not menu_item:
        return {"type": "error", "content": "Menu item not found."}
    
    # Check if item already in cart
    for item in cart_items:
        if item["menu_item_id"] == item_id:
            item["quantity"] += quantity
            break
    else:
        # Add new item to cart
        cart_items.append({
            "menu_item_id": item_id,
            "name": menu_item.name,
            "price": float(menu_item.price),
            "quantity": quantity
        })
    
    # Calculate cart total
    cart_total = sum(item["price"] * item["quantity"] for item in cart_items)
    
    return {
        "type": "cart_update",
        "content": f"Added {quantity} {menu_item.name}(s) to your cart.",
        "cart_items": cart_items,
        "cart_total": cart_total
    }

def handle_checkout(user_id: int, restaurant_id: int, cart_items: List[Dict], 
                   delivery_address: str, payment_method: str, db: Session):
    """Process the checkout and create an order"""
    
    # Convert cart items to order items format
    order_items = []
    for item in cart_items:
        order_items.append(schemas.OrderItemCreate(
            menu_item_id=item["menu_item_id"],
            quantity=item["quantity"],
            price=item["price"]
        ))
    
    # Create order request
    order_request = schemas.OrderCreate(
        user_id=user_id,
        restaurant_id=restaurant_id,
        items=order_items,
        total_amount=sum(item["price"] * item["quantity"] for item in cart_items),
        delivery_address=delivery_address,
        special_instructions=""
    )
    
    # Create the order
    try:
        order = crud.create_order(db, order_request)
        
        # Create payment record
        payment = crud.create_payment(db, schemas.PaymentCreate(
            order_id=order.id,
            amount=float(order.total_amount),
            method=payment_method,
            transaction_id=f"TR-{order.id}-{int(datetime.datetime.now().timestamp())}"
        ))
        
        return {
            "type": "order_confirmation",
            "content": f"Your order has been placed successfully!",
            "order_id": order.id,
            "order_status": order.status,
            "payment_status": payment.status,
            "estimated_delivery": "30-45 minutes"
        }
    except Exception as e:
        return {"type": "error", "content": f"Failed to create order: {str(e)}"}

def get_order_status_response(order, db: Session):
    """Generate detailed order status response"""
    # Get order items
    order_items = db.query(models.OrderItem).filter(
        models.OrderItem.order_id == order.id
    ).all()
    
    # Get payment info
    payment = db.query(models.Payment).filter(
        models.Payment.order_id == order.id
    ).first()
    
    # Format items
    items_formatted = []
    for item in order_items:
        menu_item = db.query(models.MenuItem).filter(
            models.MenuItem.id == item.menu_item_id
        ).first()
        
        items_formatted.append({
            "name": menu_item.name if menu_item else "Unknown Item",
            "quantity": item.quantity,
            "price": float(item.price),
            "total": float(item.price * item.quantity)
        })
    
    # Get restaurant
    restaurant = db.query(models.Restaurant).filter(
        models.Restaurant.id == order.restaurant_id
    ).first()
    
    return {
        "type": "order_details",
        "content": f"Here are the details for Order #{order.id}:",
        "order": {
            "id": order.id,
            "status": order.status,
            "created_at": order.order_date.isoformat(),
            "restaurant": restaurant.name if restaurant else "Unknown Restaurant",
            "items": items_formatted,
            "subtotal": sum(item["total"] for item in items_formatted),
            "delivery_fee": 5.00,
            "total": float(order.total_amount),
            "payment_status": payment.status if payment else "Not paid",
            "delivery_address": order.delivery_address
        }
    }

def handle_order_update(order_id: int, update_type: str, update_value: str, db: Session):
    """Handle order updates"""
    order = crud.get_order(db, order_id)
    if not order:
        return {"type": "error", "content": "Order not found."}
    
    if order.status not in ["pending", "confirmed"]:
        return {"type": "error", "content": "Sorry, this order cannot be modified anymore."}
    
    if update_type == "address":
        # Update delivery address
        order_update = schemas.OrderUpdate(delivery_address=update_value)
        crud.update_order(db, order_id, order_update)
        return {
            "type": "update_confirmation",
            "content": f"Your delivery address has been updated to: {update_value}"
        }
    
    elif update_type == "instructions":
        # Update special instructions
        order_update = schemas.OrderUpdate(special_instructions=update_value)
        crud.update_order(db, order_id, order_update)
        return {
            "type": "update_confirmation",
            "content": f"Your special instructions have been updated."
        }
    
    elif update_type == "cancel":
        # Cancel order
        order_update = schemas.OrderUpdate(status="cancelled")
        crud.update_order(db, order_id, order_update)
        return {
            "type": "update_confirmation",
            "content": f"Your order has been cancelled."
        }
    
    return {"type": "error", "content": "Invalid update type."}