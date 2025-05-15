# 🍔 ChatNChow 💬  
*A Modern AI-Powered Food Delivery Chatbot System*

A full-stack food delivery application with an intelligent chatbot interface that allows users to place orders, track deliveries, and manage food orders in real-time with ease.

---

## 🚀 Features

### 🛒 Order Management
- 🤖 Place new orders via conversational interface
- 📖 View restaurant menus with prices & descriptions
- 📦 Real-time order tracking
- ❌ Cancel orders with automatic refunds
- 📝 Add special delivery instructions & preferences

### 💳 Payment System
- 💵 Online payment via QR code
- 💰 Cash on Delivery (COD)
- 🔐 Secure transaction handling
- 🔄 Auto-refund processing for cancelled orders
- 📊 Payment status updates
- 

### 🌐 User Experience
- 💬 Natural language chat interface
- 🕒 View order history
- 🛑 Easy cancellations
- 🙋‍♀️ Connect with live agents if needed
- 📱 Fully responsive design for mobile/tablets

---

## 🛠️ Tech Stack

### 🔙 Backend
- ⚡ FastAPI (Python)
- 🗃️ SQLAlchemy ORM
- 🐘 PostgreSQL Database
- 🔳 QR Code Generation
- 🔁 RESTful API Architecture

### 🔜 Frontend
- ⚛️ React.js
- 🎨 Material-UI Components
- 🔄 Axios for API calls
- 🧭 React Router
- 🧠 Real-time Chat Interface
- 📱 Responsive UI

---

## 🧭 Project Structure
ChatNChow/
├── BE/ # Backend (FastAPI)
│ ├── app/
│ │ ├── models/ # DB models
│ │ ├── schemas/ # Pydantic schemas
│ │ ├── crud.py # CRUD logic
│ │ └── main.py # FastAPI app
│ └── requirements.txt
└── FE/ # Frontend (React)
├── src/
│ ├── components/
│ ├── pages/
│ └── App.js
└── package.json

---

## ⚙️ Backend Setup

```bash
cd BE
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

Create a .env file:
DATABASE_URL=postgresql://user:password@localhost:5432/chatnchow
Run the backend server:
uvicorn app.main:app --reload

---
🎨 Frontend Setup
# Navigate to the frontend directory
cd FE

# Install all dependencies
npm install

📁 Create a .env file inside the FE/ directory:
REACT_APP_API_URL=http://localhost:8000
🚀 Start the frontend development server:
npm start

📡 API Endpoints
💬 Chat Interface
POST /chat – Handle chat-based order queries

GET /get_qr_code/{order_id} – Generate QR code for payment

📦 Order Management
POST /cancel_order/{order_id} – Cancel an order

GET /orders/{order_id}/status – Check order status

🍴 Restaurants
GET /restaurants – List all restaurants

GET /restaurants/{id}/menu – Get restaurant’s menu

🗃️ Database Schema
Main Tables:

🧑 Users

🧾 Orders

🍱 OrderItems

💸 Payments

🍽️ Restaurants

🧆 MenuItems

🛵 Deliveries


📚 API Documentation
🔍 Swagger UI – Interactive API docs

📘 ReDoc – Clean API reference

🤝 Contributing
We welcome contributions! Here's how:

🍴 Fork the repository

🌿 Create a feature branch:
git checkout -b feature/YourFeature
💾 Commit your changes:
git commit -m "Add: Your feature"

🚀 Push your branch:
git push origin feature/YourFeature
📩 Open a Pull Request



📄 License
This project is licensed under the MIT License.
See the LICENSE file for details.


---



🙏 Acknowledgments
⚡ FastAPI

🧠 SQLAlchemy

⚛️ React

🎨 Material-UI





