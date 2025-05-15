# ChatNChow 🍔💬

A full-stack food delivery application built with React and FastAPI.

## Features

- Restaurant listing and menu browsing
- Real-time order tracking
- Online payment with QR code
- Cash on Delivery option
- Order management
- Responsive design

## Tech Stack

### Frontend
- React.js
- Material-UI
- Axios for API calls
- React Router for navigation

### Backend
- FastAPI
- SQLAlchemy ORM
- PostgreSQL database
- QR code generation for payments

## Project Structure

```
FoodSupport/
├── BE/                 # Backend (FastAPI)
│   ├── app/
│   │   ├── models/    # Database models
│   │   ├── schemas/   # Pydantic schemas
│   │   ├── crud.py    # CRUD operations
│   │   └── main.py    # FastAPI application
│   └── requirements.txt
└── FE/                 # Frontend (React)
    ├── src/
    │   ├── components/
    │   ├── pages/
    │   └── App.js
    └── package.json
```

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd BE
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file with:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/foodsupport
   ```

5. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd FE
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create `.env` file:
   ```
   REACT_APP_API_URL=http://localhost:8000
   ```

4. Start the development server:
   ```bash
   npm start
   ```

## Deployment

### Backend (Render)
1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:
   - `DATABASE_URL`: Your PostgreSQL database URL

### Frontend (Vercel)
1. Create a new project on Vercel
2. Connect your GitHub repository
3. Set build command: `npm run build`
4. Add environment variables:
   - `REACT_APP_API_URL`: Your Render backend URL

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 