from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime

from db.session import get_db
from db.models import Project, Category, EmptyShelf, AccessionedItem

router = APIRouter()

# Pydantic models for request/response
class CategoryCreate(BaseModel):
    name: str
    shelf_target: int
    default_items_per_shelf: int

class CategoryResponse(BaseModel):
    id: int
    name: str
    shelf_target: int
    default_items_per_shelf: int
    
    class Config:
        from_attributes = True

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    categories: List[CategoryCreate] = []

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    categories: Optional[List[CategoryCreate]] = None

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    categories: List[CategoryResponse]
    
    class Config:
        from_attributes = True

# ============================================
# PROJECT ENDPOINTS
# ============================================

@router.get("/projects", response_model=List[ProjectResponse])
def get_projects(db: Session = Depends(get_db)):
    """Get all projects"""
    projects = db.query(Project).options(joinedload(Project.categories)).all()
    return projects

@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get a specific project by ID"""
    project = db.query(Project).options(joinedload(Project.categories)).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("/projects", response_model=ProjectResponse)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """Create a new project with categories"""
    # Check if project name already exists
    existing = db.query(Project).filter(Project.name == project.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Project with this name already exists")
    
    # Create project
    db_project = Project(
        name=project.name,
        description=project.description
    )
    db.add(db_project)
    db.flush()  # Get the project ID
    
    # Create categories
    for cat in project.categories:
        db_category = Category(
            project_id=db_project.id,
            name=cat.name,
            shelf_target=cat.shelf_target,
            default_items_per_shelf=cat.default_items_per_shelf
        )
        db.add(db_category)
    
    db.commit()
    db.refresh(db_project)
    return db_project

@router.put("/projects/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, project: ProjectUpdate, db: Session = Depends(get_db)):
    """Update a project and its categories"""
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Update basic info
    if project.name is not None:
        # Check if new name conflicts with another project
        existing = db.query(Project).filter(
            Project.name == project.name,
            Project.id != project_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Project with this name already exists")
        db_project.name = project.name
    
    if project.description is not None:
        db_project.description = project.description
    
    # Update categories if provided
    if project.categories is not None:
        # Delete existing categories
        db.query(Category).filter(Category.project_id == project_id).delete()
        
        # Create new categories
        for cat in project.categories:
            db_category = Category(
                project_id=project_id,
                name=cat.name,
                shelf_target=cat.shelf_target,
                default_items_per_shelf=cat.default_items_per_shelf
            )
            db.add(db_category)
    
    db.commit()
    db.refresh(db_project)
    return db_project

@router.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Delete a project and all its data"""
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(db_project)
    db.commit()
    return {"message": "Project deleted successfully"}

# ============================================
# CATEGORY ENDPOINTS
# ============================================

@router.get("/projects/{project_id}/categories", response_model=List[CategoryResponse])
def get_categories(project_id: int, db: Session = Depends(get_db)):
    """Get all categories for a project"""
    categories = db.query(Category).filter(Category.project_id == project_id).all()
    return categories

@router.get("/projects/{project_id}/stats")
def get_project_stats(project_id: int, db: Session = Depends(get_db)):
    """Get statistics for a project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    stats = []
    for category in project.categories:
        # Count shelves by status
        total_shelves = db.query(EmptyShelf).filter(
            EmptyShelf.project_id == project_id,
            EmptyShelf.category_id == category.id
        ).count()
        
        available_shelves = db.query(EmptyShelf).filter(
            EmptyShelf.project_id == project_id,
            EmptyShelf.category_id == category.id,
            EmptyShelf.status == "available"
        ).count()
        
        accessioned_shelves = db.query(EmptyShelf).filter(
            EmptyShelf.project_id == project_id,
            EmptyShelf.category_id == category.id,
            EmptyShelf.status == "accessioned"
        ).count()
        
        stats.append({
            "category_id": category.id,
            "category_name": category.name,
            "shelf_target": category.shelf_target,
            "default_items_per_shelf": category.default_items_per_shelf,
            "total_shelves": total_shelves,
            "available_shelves": available_shelves,
            "accessioned_shelves": accessioned_shelves,
            "remaining_needed": max(0, category.shelf_target - total_shelves)
        })
    
    return {
        "project_id": project_id,
        "project_name": project.name,
        "categories": stats
    }
