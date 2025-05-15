# BE/schemas.py
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True

class MenuItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = "Other"
    image_url: Optional[str] = None

class MenuItemCreate(MenuItemBase):
    restaurant_id: int

class MenuItem(MenuItemBase):
    id: int
    restaurant_id: int
    
    class Config:
        from_attributes = True

class OrderItemBase(BaseModel):
    menu_item_id: int
    quantity: int
    price: float
    special_requests: Optional[str] = None

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(BaseModel):
    item_id: int
    name: str
    quantity: int
    price: float
    total: float
    restaurant: str

class OrderBase(BaseModel):
    user_id: int
    restaurant_id: int
    total_amount: float
    delivery_address: Optional[str] = None
    special_instructions: Optional[str] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    status: Optional[str] = None
    delivery_address: Optional[str] = None
    special_instructions: Optional[str] = None

class Order(OrderBase):
    id: int
    order_date: datetime
    status: str
    items: Optional[List[OrderItem]] = None
    
    class Config:
        from_attributes = True

class RestaurantBase(BaseModel):
    name: str
    address: str
    image_url: Optional[str] = None

class RestaurantCreate(RestaurantBase):
    pass

class Restaurant(RestaurantBase):
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True

class PaymentBase(BaseModel):
    order_id: int
    amount: float
    method: str
    transaction_id: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class Payment(PaymentBase):
    id: int
    payment_date: datetime
    status: str
    
    class Config:
        from_attributes = True

class DeliveryBase(BaseModel):
    order_id: int
    delivery_address: str
    estimated_time: Optional[datetime] = None

class DeliveryCreate(DeliveryBase):
    pass

class Delivery(DeliveryBase):
    id: int
    status: str
    delivery_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Response Models for Chat API
class ChatResponseBase(BaseModel):
    type: str
    content: str

class WelcomeResponse(ChatResponseBase):
    options: List[Dict[str, str]]

class RestaurantSelectionResponse(ChatResponseBase):
    restaurants: List[Dict[str, Any]]

class MenuDisplayResponse(ChatResponseBase):
    restaurant: Dict[str, Any]
    categories: List[Dict[str, Any]]

class CartUpdateResponse(ChatResponseBase):
    cart_items: List[Dict[str, Any]]
    cart_total: float

class OrderDetailsResponse(ChatResponseBase):
    order: Dict[str, Any]

class OrderConfirmationResponse(ChatResponseBase):
    order_id: int
    order_status: str
    payment_status: str
    estimated_delivery: str

class UpdateOptionsResponse(ChatResponseBase):
    options: List[Dict[str, str]]

class UpdateConfirmationResponse(ChatResponseBase):
    pass

class ErrorResponse(ChatResponseBase):
    pass

class DeliveryInfo(BaseModel):
    delivery_person: str
    estimated_time: datetime
    status: str

class PaymentInfo(BaseModel):
    status: str
    method: str
    amount: float

class OrderDetails(BaseModel):
    order_id: int
    customer_name: str
    order_time: datetime
    status: str
    delivery_address: str
    items: List[OrderItem]
    delivery: Optional[DeliveryInfo]
    payment: Optional[PaymentInfo]
    total_amount: float
    delivery_charge: float
    tax: float
    final_amount: float
    special_instructions: Optional[str]

    class Config:
        from_attributes = True