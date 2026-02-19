# backend/db/models.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    categories = relationship("Category", back_populates="project", cascade="all, delete-orphan")
    empty_shelves = relationship("EmptyShelf", back_populates="project", cascade="all, delete-orphan")
    accessioned_items = relationship("AccessionedItem", back_populates="project", cascade="all, delete-orphan")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)
    shelf_target = Column(Integer, nullable=False)  # Number of shelves needed
    default_items_per_shelf = Column(Integer, nullable=False)  # Default items per shelf
    
    # Relationships
    project = relationship("Project", back_populates="categories")
    empty_shelves = relationship("EmptyShelf", back_populates="category")


class EmptyShelf(Base):
    __tablename__ = "empty_shelves"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    call_number = Column(String, nullable=False, index=True)  # e.g., S-1-01B-02-03
    status = Column(String, nullable=False, default="available")  # available, accessioned
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="empty_shelves")
    category = relationship("Category", back_populates="empty_shelves")


class AccessionedItem(Base):
    __tablename__ = "accessioned_items"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    barcode = Column(String, nullable=False, index=True)
    alternative_call_number = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="accessioned_items")
