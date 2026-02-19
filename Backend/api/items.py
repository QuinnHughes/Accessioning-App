from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
import io
import pandas as pd

from db.session import get_db
from db.models import AccessionedItem

router = APIRouter()

# Pydantic models
class AccessionedItemCreate(BaseModel):
    barcode: str
    alternative_call_number: str

# ============================================
# UPLOAD/EXPORT ENDPOINTS
# ============================================

@router.post("/items/upload")
async def upload_accessioned_items(
    file: UploadFile = File(...),
    project_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """Upload Excel file with accessioned items (barcode + alternative_call_number)"""
    try:
        # Read Excel file
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # Validate columns
        required_columns = ["barcode", "alternative_call_number"]
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(
                status_code=400, 
                detail=f"Excel file must contain columns: {', '.join(required_columns)}"
            )
        
        # Process rows
        created_count = 0
        updated_count = 0
        skipped_count = 0
        errors = []
        
        for idx, row in df.iterrows():
            barcode = str(row["barcode"]).strip()
            alt_call_number = str(row["alternative_call_number"]).strip()
            
            # Skip empty rows
            if not barcode or barcode == "nan" or not alt_call_number or alt_call_number == "nan":
                skipped_count += 1
                continue
            
            try:
                # Check if item already exists
                existing = db.query(AccessionedItem).filter(
                    AccessionedItem.project_id == project_id,
                    AccessionedItem.barcode == barcode
                ).first()
                
                if existing:
                    # Update existing
                    existing.alternative_call_number = alt_call_number
                    updated_count += 1
                else:
                    # Create new
                    item = AccessionedItem(
                        project_id=project_id,
                        barcode=barcode,
                        alternative_call_number=alt_call_number
                    )
                    db.add(item)
                    created_count += 1
                
            except Exception as e:
                errors.append(f"Row {idx + 2}: {str(e)}")
        
        db.commit()
        
        return {
            "success": True,
            "items_count": created_count + updated_count,
            "created": created_count,
            "updated": updated_count,
            "skipped": skipped_count,
            "errors": errors
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")

@router.get("/items")
def get_accessioned_items(
    project_id: int = Query(...),
    start_range: Optional[str] = None,
    end_range: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get accessioned items, optionally filtered by call number range"""
    query = db.query(AccessionedItem).filter(AccessionedItem.project_id == project_id)
    
    # Apply range filter if provided
    if start_range and end_range:
        query = query.filter(
            AccessionedItem.alternative_call_number >= start_range,
            AccessionedItem.alternative_call_number <= end_range
        )
    
    items = query.order_by(AccessionedItem.alternative_call_number).all()
    
    return [
        {
            "id": item.id,
            "barcode": item.barcode,
            "alternative_call_number": item.alternative_call_number,
            "created_at": item.created_at
        }
        for item in items
    ]

@router.get("/items/export")
def export_accessioned_items(
    project_id: int = Query(...),
    start_range: Optional[str] = None,
    end_range: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Export accessioned items to Excel"""
    query = db.query(AccessionedItem).filter(AccessionedItem.project_id == project_id)
    
    # Apply range filter if provided
    if start_range and end_range:
        query = query.filter(
            AccessionedItem.alternative_call_number >= start_range,
            AccessionedItem.alternative_call_number <= end_range
        )
    
    items = query.order_by(AccessionedItem.alternative_call_number).all()
    
    # Prepare data for export
    data = []
    for item in items:
        data.append({
            "barcode": item.barcode,
            "alternative_call_number": item.alternative_call_number,
            "uploaded_at": item.created_at
        })
    
    # Create Excel file
    df = pd.DataFrame(data)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Accessioned Items")
    buffer.seek(0)
    
    # Generate filename with range if applicable
    if start_range and end_range:
        safe_start = start_range.replace("/", "-")
        safe_end = end_range.replace("/", "-")
        filename = f"project_{project_id}_items_{safe_start}_to_{safe_end}.xlsx"
    else:
        filename = f"project_{project_id}_items.xlsx"
    
    headers = {
        "Content-Disposition": f"attachment; filename={filename}"
    }
    
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers
    )

@router.delete("/items/{item_id}")
def delete_accessioned_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    """Delete an accessioned item"""
    item = db.query(AccessionedItem).filter(AccessionedItem.id == item_id).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(item)
    db.commit()
    return {"message": "Item deleted successfully"}
