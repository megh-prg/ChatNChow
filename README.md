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

## 🧽 Project Structure

```
ChatNChow/
💁🏼 BE/                  # Backend (FastAPI)
💁🏼 ├\2500 app/
💁🏼 │   ├\2500 models/      # DB models
💁🏼 │   ├\2500 schemas/     # Pydantic schemas
💁🏼 │   ├\2500 crud.py      # CRUD logic
💁🏼 │   └\2500 main.py      # FastAPI app entry point
💁🏼 └\2500 requirements.txt
💁🏼 FE/                  # Frontend (React)
    ├\2500 src/
    │   ├\2500 components/
    │   ├\2500 pages/
    │   └\2500 App.js
    └\2500 package.json
```

---

## ⚙️ Backend Setup

```bash
# Navigate to the backend directory
cd BE

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**📁 Create a `.env` file:**

```env
DATABASE_URL=postgresql://user:password@localhost:5432/chatnchow
```

**🚀 Run the FastAPI server:**

```bash
uvicorn app.main:app --reload
```

---

## 🎨 Frontend Setup

```bash
# Navigate to the frontend directory
cd FE

# Install all dependencies
npm install
```

**📁 Create a `.env` file inside `FE/`:**

```env
REACT_APP_API_URL=http://localhost:8000
```

**🚀 Start the React development server:**

```bash
npm start
```

---

## 📱 API Endpoints

### 💬 Chat Interface

* `POST /chat` – Handle chat-based order queries
* `GET /get_qr_code/{order_id}` – Generate QR code for payment

### 📦 Order Management

* `POST /cancel_order/{order_id}` – Cancel an order
* `GET /orders/{order_id}/status` – Check order status

### 🍴 Restaurants

* `GET /restaurants` – List all restaurants
* `GET /restaurants/{id}/menu` – Get restaurant’s menu

---

## 🗓️ Database Schema

Main Tables:

* 🧑 **Users**
* 📟 **Orders**
* 🍱 **OrderItems**
* 💸 **Payments**
* 🍽️ **Restaurants**
* 🫖 **MenuItems**
* 🙵️ **Deliveries**

---

## 📚 API Documentation

* 🔍 **Swagger UI** – Interactive API explorer
* 📘 **ReDoc** – Clean and professional API reference

---

## 🤝 Contributing

We welcome contributions! Here’s how you can help:

1. 🍴 Fork the repository
2. 🌿 Create a feature branch:

   ```bash
   git checkout -b feature/YourFeature
   ```
3. 📀 Commit your changes:

   ```bash
   git commit -m "Add: YourFeature"
   ```
4. 🚀 Push your branch:

   ```bash
   git push origin feature/YourFeature
   ```
5. 📩 Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License**.
See the [LICENSE](./LICENSE) file for more details.

---

## 🙏 Acknowledgments

* ⚡ [FastAPI](https://fastapi.tiangolo.com/)
* 🧠 [SQLAlchemy](https://www.sqlalchemy.org/)
* ⚛️ [React](https://reactjs.org/)
* 🎨 [Material-UI](https://mui.com/)

