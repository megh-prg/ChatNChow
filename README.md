ChatNChow 🍔💬
A modern full-stack food delivery application with an intelligent chatbot interface that helps users place orders, track deliveries, and manage food orders seamlessly.

Features
Order Management
Place new orders via conversational interface

View restaurant menus with prices and descriptions

Real-time order tracking

Cancel orders with automatic refund processing

Add special instructions and delivery preferences

Payment System
Multiple payment methods:

Online payment with QR code

Cash on Delivery (COD)

Secure payment processing

Automatic refunds for cancelled orders

Payment status tracking

Restaurant Features
Browse restaurants by cuisine

View detailed menus and reviews

See restaurant ratings

Avail special offers and promotions

User Experience
Natural language chat interface

View order history

Real-time tracking

Easy cancellation

Connect with live agents when needed

Tech Stack
Backend
FastAPI (Python)

SQLAlchemy ORM

PostgreSQL database

QR code generation

RESTful API architecture

Frontend
React.js

Material-UI components

Axios for API calls

React Router for navigation

Real-time chat interface

Responsive design

Project Structure
bash
Copy
Edit
ChatNChow/
├── BE/                 # Backend (FastAPI)
│   ├── app/
│   │   ├── models/     # Database models
│   │   ├── schemas/    # Pydantic schemas
│   │   ├── crud.py     # CRUD operations
│   │   └── main.py     # FastAPI application
│   └── requirements.txt
└── FE/                 # Frontend (React)
    ├── src/
    │   ├── components/
    │   ├── pages/
    │   └── App.js
    └── package.json
Setup Instructions
Clone the Repository
bash
Copy
Edit
git clone https://github.com/yourusername/chatnchow.git
cd chatnchow
Backend Setup
bash
Copy
Edit
cd BE
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
Set up environment variables in a .env file:

bash
Copy
Edit
DATABASE_URL=postgresql://user:password@localhost:5432/chatnchow
Run the server:

bash
Copy
Edit
uvicorn app.main:app --reload
Frontend Setup
bash
Copy
Edit
cd FE
npm install
Create a .env file in the FE directory:

ini
Copy
Edit
REACT_APP_API_URL=http://localhost:8000
Start the frontend server:

bash
Copy
Edit
npm start
API Endpoints
Chat Interface
POST /chat – Main chatbot endpoint

GET /get_qr_code/{order_id} – Generate payment QR code

Order Management
POST /cancel_order/{order_id} – Cancel an order

GET /orders/{order_id}/status – Check order status

Restaurant
GET /restaurants – List all restaurants

GET /restaurants/{id}/menu – Get a restaurant’s menu

Database Schema
Main Tables:

Users

Orders

OrderItems

Payments

Restaurants

MenuItems

Deliveries

Deployment
Backend (Render)
Create a new Web Service on Render

Connect your GitHub repository

Set build command: pip install -r requirements.txt

Set start command: uvicorn app.main:app --host 0.0.0.0 --port $PORT

Add environment variable:

DATABASE_URL: Your PostgreSQL database URL

Frontend (Vercel)
Create a new project on Vercel

Connect your GitHub repository

Set build command: npm run build

Add environment variable:

REACT_APP_API_URL: Your Render backend URL

API Documentation
Once the backend is running, visit:

Swagger UI: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc

Contributing
Fork the repository

Create your feature branch (git checkout -b feature/AmazingFeature)

Commit your changes (git commit -m 'Add some AmazingFeature')

Push to the branch (git push origin feature/AmazingFeature)

Open a Pull Request

License
This project is licensed under the MIT License - see the LICENSE file for details.

Support
Open an issue on GitHub

Use the in-app chat to connect with a real agent

Contact the team: support@chatnchow.com

Acknowledgments
FastAPI Documentation

SQLAlchemy Docs

React.js

Material-UI
