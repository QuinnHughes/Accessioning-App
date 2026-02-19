from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import PlainTextResponse, StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
import io
import pandas as pd

from db.session import get_db
from db.models import EmptyShelf, Category, AccessionedItem

router = APIRouter()

# Pydantic models
class AccessionRequest(BaseModel):
    project_id: int
    shelf_call_number: str
    item_count: int

class AccessionItem(BaseModel):
    barcode: str
    alternative_call_number: str

# ============================================
# ACCESSIONING ENDPOINTS
# ============================================

def generate_call_numbers(base_call_number: str, quantity: int) -> List[str]:
    """Generate alternative call numbers for a shelf"""
    # Format: S-1-01B-02-03-001
    # We need to add positions (last segment)
    call_numbers = []
    for i in range(1, quantity + 1):
        call_number = f"{base_call_number}-{i:03d}"
        call_numbers.append(call_number)
    return call_numbers

@router.post("/accession/generate-excel")
def generate_accession_excel(
    request: AccessionRequest,
    db: Session = Depends(get_db)
):
    """Generate Excel preview data for accessioning"""
    # Verify shelf exists in this project
    shelf = db.query(EmptyShelf).filter(
        EmptyShelf.project_id == request.project_id,
        EmptyShelf.call_number == request.shelf_call_number
    ).first()
    
    if not shelf:
        raise HTTPException(status_code=404, detail="Shelf not found in this project")
    
    # Generate call numbers
    call_numbers = generate_call_numbers(request.shelf_call_number, request.item_count)
    
    # Return preview data
    rows = []
    for call_number in call_numbers:
        rows.append({
            "barcode": "",
            "alternative_call_number": call_number
        })
    
    return {"rows": rows}

@router.post("/accession/download-excel")
def download_accession_excel(
    request: AccessionRequest,
    db: Session = Depends(get_db)
):
    """Download Excel file for accessioning with empty barcode column"""
    # Verify shelf exists in this project
    shelf = db.query(EmptyShelf).filter(
        EmptyShelf.project_id == request.project_id,
        EmptyShelf.call_number == request.shelf_call_number
    ).first()
    
    if not shelf:
        raise HTTPException(status_code=404, detail="Shelf not found in this project")
    
    # Generate call numbers
    call_numbers = generate_call_numbers(request.shelf_call_number, request.item_count)
    
    # Create DataFrame
    data = {
        "barcode": [""] * len(call_numbers),
        "alternative_call_number": call_numbers
    }
    df = pd.DataFrame(data)
    
    # Create Excel file
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Accession")
    buffer.seek(0)
    
    # Clean filename
    safe_call_number = request.shelf_call_number.replace("/", "-")
    headers = {
        "Content-Disposition": f"attachment; filename=accession_{safe_call_number}.xlsx"
    }
    
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers
    )

@router.post("/accession/generate-labels")
def generate_accession_labels(
    request: AccessionRequest,
    db: Session = Depends(get_db)
):
    """Generate batch print format for stickers"""
    # Verify shelf exists in this project
    shelf = db.query(EmptyShelf).filter(
        EmptyShelf.project_id == request.project_id,
        EmptyShelf.call_number == request.shelf_call_number
    ).first()
    
    if not shelf:
        raise HTTPException(status_code=404, detail="Shelf not found in this project")
    
    # Generate call numbers
    call_numbers = generate_call_numbers(request.shelf_call_number, request.item_count)
    
    # Format for batch printing
    lines = []
    for call_number in call_numbers:
        lines.append(f"{call_number}\n\n\n===============")
    
    return {"labels": "\n".join(lines)}

class AdditionalLabelsRequest(BaseModel):
    project_id: int
    shelf_call_number: str
    current_item_count: int
    additional_count: int

@router.post("/accession/generate-additional-labels")
def generate_additional_labels(
    request: AdditionalLabelsRequest,
    db: Session = Depends(get_db)
):
    """Generate additional stickers starting from a specific position"""
    # Verify shelf exists in this project
    shelf = db.query(EmptyShelf).filter(
        EmptyShelf.project_id == request.project_id,
        EmptyShelf.call_number == request.shelf_call_number
    ).first()
    
    if not shelf:
        raise HTTPException(status_code=404, detail="Shelf not found in this project")
    
    # Generate additional call numbers
    call_numbers = []
    for i in range(request.current_item_count + 1, request.current_item_count + request.additional_count + 1):
        call_number = f"{request.shelf_call_number}-{i:03d}"
        call_numbers.append(call_number)
    
    # Format for batch printing
    lines = []
    for call_number in call_numbers:
        lines.append(f"{call_number}\n\n\n===============")
    
    return {"labels": "\n".join(lines)}
