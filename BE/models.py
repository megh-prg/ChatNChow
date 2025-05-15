# BE/models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from BE.base import Base
from datetime import datetime


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")


class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id', ondelete='SET NULL'), nullable=True)
    items = Column(JSON)  # Store as JSON array
    total = Column(Float)
    status = Column(String, default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="orders")
    restaurant = relationship("Restaurant", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payment = relationship("Payment", back_populates="order", uselist=False, cascade="all, delete-orphan")
    delivery = relationship("Delivery", back_populates="order", uselist=False, cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = 'order_items'
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    menu_item_id = Column(Integer, ForeignKey('menu_items.id', ondelete='SET NULL'), nullable=True)
    quantity = Column(Integer)
    price = Column(Float(precision=10))
    
    order = relationship("Order", back_populates="order_items")
    menu_item = relationship("MenuItem", back_populates="order_items")

class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    amount = Column(Float(precision=10))
    payment_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default='pending')
    method = Column(String, default='online')
    transaction_id = Column(String, nullable=True)
    
    order = relationship("Order", back_populates="payment")

class Delivery(Base):
    __tablename__ = 'deliveries'
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    delivery_address = Column(String)
    delivery_date = Column(DateTime)
    status = Column(String, default='pending')
    
    order = relationship("Order", back_populates="delivery")

class Restaurant(Base):
    __tablename__ = 'restaurants'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    address = Column(String)
    cuisine = Column(String)
    rating = Column(Float, default=0.0)
    image_url = Column(String)  # Add this for restaurant images
    is_active = Column(Boolean, default=True)
    orders = relationship("Order", back_populates="restaurant")
    menu_items = relationship("MenuItem", back_populates="restaurant", cascade="all, delete-orphan")

class MenuItem(Base):
    __tablename__ = 'menu_items'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Float(precision=10))
    image_url = Column(String)  # Add this for menu item images
    category = Column(String)   # Add category (e.g., "Appetizers", "Main Course")
    restaurant_id = Column(Integer, ForeignKey('restaurants.id', ondelete='CASCADE'), nullable=False)
    restaurant = relationship("Restaurant", back_populates="menu_items")
    order_items = relationship("OrderItem", back_populates="menu_item")

