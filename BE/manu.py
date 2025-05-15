# routers/menu.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .database import get_db
from . import models

router = APIRouter(prefix="/menu", tags=["menu"])

class Restaurant(Base):
    __tablename__ = 'restaurants'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    address = Column(String)

class MenuItem(BaseModel):
    id: int
    name: str
    description: str
    price: float
    category: str

@router.get("", response_model=List[MenuItem])
def get_menu(db: Session = Depends(get_db)):
    """Get all available menu items"""
    return db.query(models.MenuItem).all()