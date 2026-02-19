from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Dict

from db.session import get_db
from db.models import EmptyShelf, Category

router = APIRouter()

# Pydantic models
class ShelfConfig(BaseModel):
    shelf_id: int
    item_count: int

class BatchPrintRequest(BaseModel):
    project_id: int
    shelf_configs: List[ShelfConfig]

# ============================================
# BATCH PRINTING ENDPOINTS
# ============================================

def generate_call_numbers_for_shelf(base_call_number: str, quantity: int) -> List[str]:
    """Generate alternative call numbers for a shelf"""
    call_numbers = []
    for i in range(1, quantity + 1):
        call_number = f"{base_call_number}-{i:03d}"
        call_numbers.append(call_number)
    return call_numbers

@router.post("/batch-print/generate")
def generate_batch_labels(
    request: BatchPrintRequest,
    db: Session = Depends(get_db)
):
    """Generate batch print labels for multiple shelves"""
    all_labels = []
    
    for shelf_config in request.shelf_configs:
        # Get shelf
        shelf = db.query(EmptyShelf).filter(
            EmptyShelf.id == shelf_config.shelf_id,
            EmptyShelf.project_id == request.project_id
        ).first()
        
        if not shelf:
            raise HTTPException(status_code=404, detail=f"Shelf {shelf_config.shelf_id} not found")
        
        # Generate call numbers for this shelf
        call_numbers = generate_call_numbers_for_shelf(shelf.call_number, shelf_config.item_count)
        
        # Add to batch
        for call_number in call_numbers:
            all_labels.append(f"{call_number}\n\n\n===============")
    
    # Reverse labels for printer (first label at end, last label at start)
    all_labels.reverse()
    
    return {"labels": "\n".join(all_labels)}

@router.get("/batch-print/shelf-defaults/{shelf_id}")
def get_shelf_defaults(
    shelf_id: int,
    db: Session = Depends(get_db)
):
    """Get default quantity for a shelf"""
    shelf = db.query(EmptyShelf).filter(EmptyShelf.id == shelf_id).first()
        
    if not shelf:
        raise HTTPException(status_code=404, detail="Shelf not found")
    
    category = db.query(Category).filter(Category.id == shelf.category_id).first()
    
    return {
        "shelf_id": shelf.id,
        "call_number": shelf.call_number,
        "category_name": category.name if category else "Unknown",
        "default_items_per_shelf": category.default_items_per_shelf if category else 25,
        "status": shelf.status
    }
