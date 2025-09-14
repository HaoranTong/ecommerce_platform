#!/usr/bin/env python3
"""Debug script to check model imports and table creation"""

import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Import Base first
from app.core.database import Base

# Import all models
print("Importing models...")
from app.modules.product_catalog.models import (
    Category, Brand, Product, SKU, ProductAttribute, 
    SKUAttribute, ProductImage, ProductTag
)
from app.modules.user_auth.models import User, Role, Permission, UserRole, RolePermission, Session

print("Models imported successfully!")

# Check what tables are registered
print(f"\nRegistered tables: {Base.metadata.tables.keys()}")

# Create an in-memory SQLite engine to test
from sqlalchemy import create_engine
engine = create_engine("sqlite:///:memory:")

print("\nCreating tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")

# List created tables
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"Created tables: {tables}")