from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import io
import pandas as pd
from fastapi.responses import StreamingResponse

from db.session import get_db
from db.models import EmptyShelf, Category, Project

router = APIRouter()

# Pydantic models
class EmptyShelfCreate(BaseModel):
    project_id: int
    call_number: str
    category_id: int

class EmptyShelfUpdate(BaseModel):
    status: str  # available or accessioned

class EmptyShelfResponse(BaseModel):
    id: int
    project_id: int
    category_id: int
    call_number: str
    status: str
    category_name: Optional[str] = None
    
    class Config:
        from_attributes = True

# ============================================
# EMPTY SHELF ENDPOINTS
# ============================================

@router.get("/shelves", response_model=List[EmptyShelfResponse])
def get_empty_shelves(
    project_id: int = Query(...),
    category_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all empty shelves for a project, optionally filtered by category and status"""
    query = db.query(EmptyShelf).filter(EmptyShelf.project_id == project_id)
    
    if category_id:
        query = query.filter(EmptyShelf.category_id == category_id)
    
    if status:
        query = query.filter(EmptyShelf.status == status)
    
    shelves = query.options(joinedload(EmptyShelf.category)).order_by(EmptyShelf.call_number).all()
    
    # Manually add category_name to response
    result = []
    for shelf in shelves:
        shelf_dict = {
            "id": shelf.id,
            "project_id": shelf.project_id,
            "category_id": shelf.category_id,
            "call_number": shelf.call_number,
            "status": shelf.status,
            "category_name": shelf.category.name if shelf.category else "Unknown"
        }
        result.append(shelf_dict)
    
    return result

@router.post("/shelves", response_model=EmptyShelfResponse)
def create_empty_shelf(
    shelf: EmptyShelfCreate,
    db: Session = Depends(get_db)
):
    """Add a new empty shelf to a project"""
    # Verify project exists
    project = db.query(Project).filter(Project.id == shelf.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Verify category exists and belongs to this project
    category = db.query(Category).filter(
        Category.id == shelf.category_id,
        Category.project_id == shelf.project_id
    ).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found or doesn't belong to this project")
    
    # Check if shelf already exists in this project
    existing = db.query(EmptyShelf).filter(
        EmptyShelf.project_id == shelf.project_id,
        EmptyShelf.call_number == shelf.call_number
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="This shelf is already recorded for this project")
    
    # Create shelf
    db_shelf = EmptyShelf(
        project_id=shelf.project_id,
        category_id=shelf.category_id,
        call_number=shelf.call_number,
        status="available"
    )
    db.add(db_shelf)
    db.commit()
    db.refresh(db_shelf)
    
    return db_shelf

@router.patch("/shelves/{shelf_id}/status", response_model=EmptyShelfResponse)
def update_shelf_status(
    shelf_id: int,
    shelf: EmptyShelfUpdate,
    db: Session = Depends(get_db)
):
    """Update shelf status (mark as accessioned or available)"""
    db_shelf = db.query(EmptyShelf).filter(EmptyShelf.id == shelf_id).first()
    
    if not db_shelf:
        raise HTTPException(status_code=404, detail="Shelf not found")
    
    # Validate status
    if shelf.status not in ["available", "accessioned"]:
        raise HTTPException(status_code=400, detail="Status must be 'available' or 'accessioned'")
    
    db_shelf.status = shelf.status
    db.commit()
    db.refresh(db_shelf)
    
    return db_shelf

@router.delete("/shelves/{shelf_id}")
def delete_shelf(shelf_id: int, db: Session = Depends(get_db)):
    """Delete a shelf"""
    db_shelf = db.query(EmptyShelf).filter(EmptyShelf.id == shelf_id).first()
    
    if not db_shelf:
        raise HTTPException(status_code=404, detail="Shelf not found")
    
    db.delete(db_shelf)
    db.commit()
    return {"message": "Shelf deleted successfully"}

@router.get("/shelves/export")
def export_shelves(
    project_id: int = Query(...),
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Export shelves to Excel"""
    query = db.query(EmptyShelf).filter(EmptyShelf.project_id == project_id)
    
    if status:
        query = query.filter(EmptyShelf.status == status)
    
    shelves = query.options(joinedload(EmptyShelf.category)).order_by(EmptyShelf.call_number).all()
    
    # Prepare data for export
    data = []
    for shelf in shelves:
        data.append({
            "Call Number": shelf.call_number,
            "Category": shelf.category.name if shelf.category else "Unknown",
            "Status": shelf.status
        })
    
    # Create Excel file
    df = pd.DataFrame(data)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Empty Shelves")
    buffer.seek(0)
    
    headers = {
        "Content-Disposition": f"attachment; filename=project_{project_id}_shelves.xlsx"
    }
    
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers
    )
