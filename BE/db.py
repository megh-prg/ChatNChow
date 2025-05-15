def test_connection():
    db = SessionLocal()
    try:
        print(db.query(models.User).first())  
    finally:
        db.close()